#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014. 06. 09
@author: <mwpark@castis.com>
'''
import argparse
import datetime
import fileinput
import json
import os
import re
import signal
import sys
import time

import chardet
from dateutil import parser

program_version = "0.1.3"

# Ensure print function compatibility
from __future__ import print_function

colors = {
    "id": '\033[0;36m',
    "event": '\033[0;38;05;118m',
    "date": '\033[0;34m',
    "time": '\033[0;36m',
    "level": '\033[0;38;05;81m',
    "section": '\033[0;38;05;208m',
    "code": '\033[0;32m',
    "description": '\033[0m',
    "error": '\033[0;31m',
    "number": '\033[0;38;05;141m',
    "keyword": '\033[0;95m',
    "key_value": '\033[0;96m',
    "where":   '\033[0;33m',
    "request":   '\033[0;32m',
    "status_code":   '\033[0;93m',
    "ip":   '\033[0;95m',
    "user_name":   '\033[0;96m',
    "verbose": '\033[0;38;05;118m',
    "debug": '\033[0;38;05;118m'
}

ansi_colors = {
    "default": '\033[0m', # reset
    "black": '\033[0;30m',
    "red": '\033[0;31m',
    "green": '\033[0;32m',
    "yellow": '\033[0;33m',
    "blue": '\033[0;34m',
    "magenta": '\033[0;35m',
    "cyan": '\033[0;36m',
    "white": '\033[0;37m',
    "bright_black": '\033[0;90m',
    "bright_red": '\033[0;91m',
    "bright_green": '\033[0;92m',
    "bright_yellow": '\033[0;93m',
    "bright_blue": '\033[0;94m',
    "bright_magenta": '\033[0;95m',
    "bright_cyan": '\033[0;96m',
    "bright_white": '\033[0;97m',
}

def set_256_colors():
    for i in range(16, 256):
        ansi_colors['color_{}'.format(i)] = '\033[38;5;{}m'.format(i)

event_type_major = {
    0x010000: 'SU',
    0x020000: 'RTSP-L',
    0x040000: 'RTSP-S',
    0x080000: 'SM',
    0x100000: 'FM',
    0x200000: 'FSMP',
    0x400000: 'Global'}

session_event_type = {
    0x0001: 'create',
    0x0002: 'close',
    0x0004: 'ff',
    0x0008: 'rw',
    0x0010: 'slow',
    0x0020: 'pause',
    0x0040: 'play',
    0x0080: 'teardown',
    0x0100: 'seek',
    0x0200: 'usage'}

event_level = {
    1: 'none',
    2: 'debug',
    4: 'report',
    8: 'info',
    16: 'success',
    32: 'warning',
    64: 'error',
    128: 'fail',
    256: 'except'}

class Options:
    def __init__(self):
        self.keyword_coloring = False
        self.keyvalue_coloring = False
        self.cat = False
        self.debug = False
        self.verbose = False
        self.retry = False
        self.skip_name = False
        self.skip_id = False
        self.skip_date = False
        self.skip_time = False
        self.skip_level = False
        self.skip_section = False
        self.skip_code = False
        self.print_simple_format = False
        self.follow_file = False
        self.fileoffset_repository = {}
        self.last_target_filename = ""
        self.colors = True
        self.color_file = None

_fileoffset_repository = {}

def put_offset(filename, offset):
    global _fileoffset_repository
    _fileoffset_repository[filename] = offset


def get_offset(filename):
    global _fileoffset_repository
    try:
        offset = _fileoffset_repository[filename]
        return offset
    except Exception as e:
        return 0

def apply_color(text, color_name):
    ansi_code = colors.get(color_name, '\033[0m')
    return "{}{}{}".format(ansi_code, text, '\033[0m')

def print_verbose(text):
    print(apply_color(text, 'verbose'))
    
def verbose(heading, message, options):
    if options.verbose:
        print_verbose('{}: {}'.format(heading, message))

def print_debug(text):
    print(apply_color(text, 'debug'))

def debug(heading, message, options):
    if options.debug:
        print_debug('{}: {}'.format(heading, message))

def get_event_type_string(event):
    try:
        s = event_type_major[int(event, 0) & 0xFFFF0000]
        if s == 'SU':
            s = s + '/' + session_event_type[int(event, 0) & 0xFFFF]
        return s
    except Exception as e:
        return ''


def get_event_level_string(level):
    try:
        s = event_level[int(level)]
        return s
    except Exception as e:
        return ''


def get_time_string_gmt_to_kst(timestamp):
    try:
        s = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(timestamp)+32400))
        return s, False, ""
    except Exception as e:
        return '', False, str(e)


def translate(log):
    try:
        event, level, datetime, description = log.split(',', 3)
    except Exception as e:
        return log, False, str(e)
    
    event = get_event_type_string(event)
    level = get_event_level_string(level)
    datetime, error, msg = get_time_string_gmt_to_kst(datetime)
    if error:
        return '', True, msg

    return ','.join([event, level, datetime, description]), False, ""


def key_value_coloring(match):
    return apply_color(match.group(), 'key_value')

def key_word_coloring(match):
    return apply_color(match.group(), 'keyword')

def format_eventlog(log, options):
    if log.startswith('0x'):
        log, error, msg = translate(log)
        if error:
            return log, True, msg
    else:
        return log, True, "Not eventlog format, does not start with '0x'"

    try:
        event, level, datetime, description = log.split(',', 3)
    except Exception as e:
        return log, True, str(e)
    
    if level.strip("[] ").lower() in ['severe', 'error', 'fail', 'warning', 'exception', 'except', 'critical']:
        level = apply_color(level,'error')
    else:
        level = apply_color(level, 'level')

    event = apply_color(event, 'event')
    
    if options.keyword_coloring:
        description = re.sub(r"\[([^]]+)\]", key_word_coloring, description)
        description = re.sub(r"\(([^)]+)\)", key_word_coloring, description)

    if options.keyvalue_coloring:
        description = re.sub(r"[a-zA-Z0-9_\-]+\s?=\s?[a-zA-Z0-9_/@$#%&\.\^\-\[\]]+", key_value_coloring, description)

    description = apply_color(description, 'description')

    if options.skip_date and options.skip_time:
        datetime = ""

    if options.skip_level:
        level = ""

    if options.print_simple_format:
        return '{} {} {} {}'.format(level, datetime, event, description), False, ""

    return '{} {} {} {}'.format(datetime, event, level, description), False, ""

def format_cilog(log, options):
    try:
        name, id, date, time, level, section, code, description = log.split(',', 7)
    except Exception as e:
        return log, True, str(e)
    
    name = apply_color(name, 'name')
    if options.skip_name:
        name = ""

    id = apply_color(id, 'id')
    if options.skip_id:
        id = ""

    if is_valid_date(date + ' ' + time) is None:
        return log, True, "Invalid date time format"
    
    date = apply_color(date, 'date')
    if options.skip_date:
        date = ""

    time = apply_color(time, 'time')
    if options.skip_time:
        time = ""

    if level.strip("[] ").lower() in ['severe', 'error', 'fail', 'warning', 'exception', 'except', 'critical']:
        level = apply_color(level, 'error')
    else:
        level = apply_color(level, 'level')
    if options.skip_level:
        level = ""

    section = apply_color(section, 'section')
    if options.skip_section:
        section = ""

    code = apply_color(code, 'code')
    if options.skip_code:
        code = ""

    if options.keyword_coloring:
        description = re.sub(r"\[([^]]+)\]", key_word_coloring, description)
        description = re.sub(r"\(([^)]+)\)", key_word_coloring, description)

    if options.keyvalue_coloring:
        description = re.sub(r"[a-zA-Z0-9_\-]+\s?=\s?[a-zA-Z0-9_/@$#%&\.\^\-\[\]]+", key_value_coloring, description)

    description = apply_color(description, 'description')

    if options.print_simple_format:
        return ','.join([level, date, time, section, code, description]), False, ""

    return ','.join([name, id, date, time, level, section, code, description]), False, ""


def is_ncsa_combined_log(log_line):
    pattern = re.compile(r'^(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\d+|-) "(.*?)" "(.*?)"$')
    match = pattern.match(log_line)
    return match is not None

def is_valid_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True

def is_valid_ncsa_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%d/%b/%Y:%H:%M:%S %z")
        return True
    except ValueError:
        return False

def format_ncsacombinedlog(log, options):
    try:
        host, id, username, datetime, tz, method, uri, version, statuscode, bytes, combined = log.split(' ', 10)
    except Exception as e:
        return log, True, str(e)
    
    if not is_valid_ip(host):
        return log, True, "Invalid IP address"
    
    if not datetime.startswith('[') or not tz.endswith(']'):
        return log, True, "Invalid datetime format"
    
    date_str = '{} {}'.format(datetime, tz).strip('[]')
    if not is_valid_ncsa_date(date_str):
        return log, True, "Invalid date format"
    
    host = apply_color(host, 'ip')
    id = apply_color(id, 'id')
    username = apply_color(username, 'user_name')
    datetimetz = apply_color('{} {}'.format(datetime, tz), 'date')
    request = "{} {} {}".format(method, uri, version)
    request = apply_color(request, 'request')
    statuscode = apply_color(statuscode, 'status_code')
    bytes = apply_color(bytes, 'number')

    if options.skip_date and options.skip_time:
        datetimetz = ""

    if options.print_simple_format:
        return '{} {} {} {} {}'.format(datetimetz, request, statuscode, bytes, combined), False, ""
    
    return '{} {} {} {} {} {} {} {}'.format(host, id, username, datetimetz, request, statuscode, bytes, combined), False, ""


def format_ncsalog(log, options):
    try:
        host, id, username, datetime, tz, method, uri, version, statuscode, bytes = log.split(' ', 9)
    except Exception as e:
        return log, True, str(e)
    
    if not is_valid_ip(host):
        return log, True, "Invalid IP address"
    
    if not datetime.startswith('[') or not tz.endswith(']'):
        return log, True, "Invalid datetime format"
    
    date_str = '{} {}'.format(datetime, tz).strip('[]')
    if not is_valid_ncsa_date(date_str):
        return log, True, "Invalid date format"
    
    host = apply_color(host, 'ip')
    id = apply_color(id, 'id')
    username = apply_color(username, 'user_name')
    datetimetz = apply_color('{} {}'.format(datetime, tz), 'date')
    request = "{} {} {}".format(method, uri, version)
    request = apply_color(request, 'request')
    statuscode = apply_color(statuscode, 'status_code')
    bytes = apply_color(bytes, 'number')

    if options.skip_date and options.skip_time:
        datetimetz = ""

    if options.print_simple_format:
        return '{} {} {} {}'.format(datetimetz, request, statuscode, bytes), False, ""

    return '{} {} {} {} {} {} {}'.format(host, id, username, datetimetz, request, statuscode, bytes), False, ""


def format_simple_log4j(log, options):
    try:
        datetime_str, level, rest = log.split(',', 2)
        section, description = rest.split(':', 1)
        date, time = datetime_str.split(' ', 1)
    except Exception as e:
        return log, True, str(e)
    
    date = apply_color(date, 'date')
    time = apply_color(time, 'time')

    if level.strip("[] ").lower() in ['severe', 'error', 'fail', 'warning', 'exception', 'except', 'critical']:
        level = apply_color(level, 'error')
    else:
        level = apply_color(level, 'level')

    section = apply_color(section, 'where')

    if options.keyword_coloring:
        description = re.sub(r"\[([^]]+)\]", key_word_coloring, description)
        description = re.sub(r"\(([^)]+)\)", key_word_coloring, description)

    if options.keyvalue_coloring:
        description = re.sub(r"[a-zA-Z0-9_\-]+\s?=\s?[a-zA-Z0-9_/@$#%&\.\^\-\[\]]+", key_value_coloring, description)

    description = apply_color(description, 'description')

    if options.skip_date:
        date = ""

    if options.skip_time:
        time = ""

    if options.skip_level:
        level = ""

    if options.skip_section:
        section = ""
    
    if options.print_simple_format:
        return '{},{},{}:{}:{}'.format(level, date, time, section, description), False, ""
    
    return '{} {},{},{},{}'.format(date, time, level, section, description), False, ""


def is_valid_date(date_str):
    try:
        date_obj = parser.parse(date_str)
        return date_obj
    except ValueError:
        return None

def format_tomcat_log(log, options):
    try:
        date, time, level, section, where, description = log.split(' ', 5)
    except Exception as e:
        return log, True, str(e)
    
    if is_valid_date('{} {}'.format(date, time)) is None:
        return log, True, 'invalid date'

    date = apply_color(date, 'date')
    time = apply_color(time, 'time')
    if level.strip("[] ").lower() in ['severe', 'error', 'fail', 'warning', 'exception', 'except', 'critical']:
        level = apply_color(level, 'error')
    else:
        level = apply_color(level, 'level')
    section = apply_color(section, 'section')
    where = apply_color(where, 'where')

    if options.keyword_coloring:
        description = re.sub(r"\[([^]]+)\]", key_word_coloring, description)
        description = re.sub(r"\(([^)]+)\)", key_word_coloring, description)

    if options.keyvalue_coloring:
        description = re.sub(r"[a-zA-Z0-9_\-]+\s?=\s?[a-zA-Z0-9_/@$#%&\.\^\-\[\]]+", key_value_coloring, description)
        
    description = apply_color(description, 'description')

    if options.skip_date:
        date = ""
    if options.skip_time:
        time = ""
    if options.skip_level:
        level = ""
    if options.skip_section:
        section = ""
    
    if options.print_simple_format:
        return '{} {} {} {} {} {}'.format(level, date, time, section, where, description), False, ""

    return '{} {} {} {} {} {}'.format(date, time, level, section, where, description), False, ""

def format_simplelog(log, options):
    try:
        level, date, time, section, description = log.split(' ', 4)
    except Exception as e:
        return log, True, str(e)
    
    if is_valid_date('{} {}'.format(date, time)) is None:
        return log, True, "Invalid date time format"
  
    date = apply_color(date, 'date')
    if options.skip_date:
        date = ""

    time = apply_color(time, 'time')
    if options.skip_time:
        time = ""

    if level.strip("[] ").lower() in ['severe', 'error', 'fail', 'warning', 'exception', 'except', 'critical']:
        level = apply_color(level, 'error')
    else:
        level = apply_color(level, 'level')
    if options.skip_level:
        level = ""

    section = apply_color(section, 'section')
    if options.skip_section:
        section = ""

    if options.keyword_coloring:
        description = re.sub(r"\[([^]]+)\]", key_word_coloring, description)
        description = re.sub(r"\(([^)]+)\)", key_word_coloring, description)

    if options.keyvalue_coloring:
        description = re.sub(r"[a-zA-Z0-9_\-]+\s?=\s?[a-zA-Z0-9_/@$#%&\.\^\-\[\]]+", key_value_coloring, description)

    description = apply_color(description, 'description')
    
    return ' '.join([level, date, time, section, description]), False, ""

def format_simple_trace(log, options):
    if options.keyword_coloring:
        log = re.sub(r"\[([^]]+)\]", key_word_coloring, log)
        log = re.sub(r"\(([^)]+)\)", key_word_coloring, log)

    if options.keyvalue_coloring:
        log = re.sub(r"[a-zA-Z0-9_\-]+\s?=\s?[a-zA-Z0-9_/@$#%&\.\^\-\[\]]+", key_value_coloring, log)

    return log, False, ""

def print_format_log(log, options):

    def try_format(log, formatter, log_type):
        formatted_log, error, msg = formatter(log, options)
        if error:
            debug('Format Info', 'NOT {}, msg: {}'.format(log_type, msg), options)
        else:
            debug('Format Info', log_type, options)

        return formatted_log, error

    formatters = [
        (format_eventlog, 'EVENTLOG'),
        (format_cilog, 'CILOG'),
        (format_ncsacombinedlog, 'NCSACOMBINE'),
        (format_ncsalog, 'NCSA'),
        (format_simple_log4j, 'LOG4J'),
        (format_tomcat_log, 'TOMCAT'),
        (format_simplelog, 'SIMPLE'),
        (format_simple_trace, 'TRACE')
    ]

    for formatter, log_type in formatters[1:]:
        formatted_log, error = try_format(log, formatter, log_type)
        if not error:
            break
    try:
        print(formatted_log, end=' ')
    except IOError:
        exit(1)
    except Exception:
        exit(1)

def is_binary(filename):
    with open(filename, 'rb') as f:
        CHUNKSIZE = 1024
        max_bytes_to_read = 4096
        bytes_read = 0

        while bytes_read < max_bytes_to_read:
            chunk = f.read(CHUNKSIZE)
            if b'\0' in chunk:
                return True
            if len(chunk) < CHUNKSIZE:
                break
    return False

def newest_file_in(path):
    newest_file_name = ""
    newest_mtime = -1

    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        if os.path.isfile(file_path):
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > newest_mtime and not is_binary(file_path):
                    newest_mtime = mtime
                    newest_file_name = file_path
            except OSError:
                continue

    return newest_file_name

def get_path_of(filename):
    path = os.path.realpath(filename)
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    return path

def exist_file(filename):
    return os.path.exists(filename) and os.path.isfile(filename)

def exist_directory(directory):
    return os.path.exists(directory)

def cat(options):
    for line in fileinput.input("-"):
        print_format_log(line, options)

def cat_file(filename, options):
    target, exist, inode = get_tail_filename(filename, True, options)
    if not exist:
        return
    
    filename = target
    encoding = detect_file_encoding(filename)
    verbose('Open', '{}, detected encoding is {}'.format(filename, encoding), options)
    
    try:
        f = open(filename, 'r', encoding=encoding, errors='replace')
    except Exception as e:
        verbose('Open Error', '{}, {}'.format(filename, e), options)
        return

    for line in f:
        print_format_log(line, options)

    return

def get_tail_filename(filename, follow_file, options):
    filename = os.path.abspath(filename)
    if follow_file:
        try:
            if not exist_file(filename):
                verbose('Error', 'Not found: {}'.format(filename), options)
                return None, False, None
            
            if is_binary(filename):
                verbose('Info', 'Not a text file: {}'.format(filename), options)
                return None, False, None

            return filename, True, os.stat(filename).st_ino

        except Exception as e:
            verbose('Error', '{}, {}'.format(filename, e), options)
            return None, False, None
    
    try:
        path = get_path_of(filename)
        if not exist_directory(path):
            verbose('Info', 'Not found path: {}'.format(path), options)
            return None, False, None
        
        tail_file = newest_file_in(path)
        if tail_file == "":
            verbose('Info', 'No text files in {}'.format(path), options)
            return None, False, None
        
        return tail_file, True, os.stat(tail_file).st_ino
    
    except Exception as e:
        verbose('Error', '{}, {}'.format(filename, e), options)
        return None, False, None

def keep_tail(f, options):
    while True:
        try:
            line = f.readline()
        except Exception as e:
            verbose('Error', '{}'.format(e), options)
            f.close()
            return 0, True
        if line:
            print_format_log(line, options)
        else:
            break
    offset = f.tell()
    return offset, False

def detect_file_encoding(file_path):
    CHUNKSIZE = 1024
    with open(file_path, 'rb') as f:
        rawdata = f.read(CHUNKSIZE)
    result = chardet.detect(rawdata)
    return result['encoding']

def open_tail(filename, options, offset=0):
    encoding = detect_file_encoding(filename)
    verbose('Open', '{}, detected encoding is {}'.format(filename, encoding), options)
    
    try:
        f = open(filename, 'r', encoding=encoding, errors='replace')
    except Exception as e:
        verbose('Open Error', '{}, {}'.format(filename, e), options)
        return None, True
    try:
        size = os.path.getsize(filename)
        if options.follow_file:
            verbose('Open', '{}, size: {:,}'.format(filename, size), options)
        else:
            path = get_path_of(filename)
            verbose('Open','{} in {}, size: {:,}'.format(filename, path, size), options)

        if offset > 0:
            f.seek(offset, 0)
        else:
            if size > 2048:
                f.seek(size - 2048 - 1, 0)
                f.readline()
    except Exception as e:
        f.close()
        verbose('Error', '{}, {}'.format(filename, e), options)

        return None, True
    return f, False


def is_inode_changed(file, inode, options):
    try:
        new_inode = os.stat(file).st_ino
        if inode != new_inode:
            return True, None
        return False, None
    except Exception as e:
        verbose('Error', '{}, {}'.format(file, e), options)

        return None, True

def tail(filename, options):
    follow_file = options.follow_file
    target, exist, inode = get_tail_filename(filename, follow_file, options)
    if not exist:
        return

    f, error = open_tail(target, options)
    if error:
        return
    options.last_target_filename = target

    while True:
        offset, error = keep_tail(f, options)
        if error:
            clean_up(inode, f, 0)
            return

        if follow_file:
            if handle_follow_file(f, target, inode, offset, options) is False:
                return
        else:
            if handle_non_follow_file(f, filename, target, inode, offset, options) is False:
                return

        time.sleep(0.1)

def clean_up(inode, file_obj, offset):
    put_offset(str(inode), offset)
    file_obj.close()

def handle_follow_file(f, target, inode, offset, options):
    is_changed, error = is_inode_changed(target, inode, options)
    if error:
        clean_up(inode, f, 0)
        return False

    if not is_changed:
        return None

    new_target, exist, new_inode = get_tail_filename(target, True, options)
    if not exist:
        clean_up(inode, f, offset)
        return False

    if inode != new_inode:
        clean_up(inode, f, offset)

        inode = new_inode
        offset = get_offset(str(inode))
        f, error = open_tail(new_target, options, offset)
        if error:
            clean_up(inode, f, 0)
            return False
        options.last_target_filename = new_target
    return None

def handle_non_follow_file(f, filename, target, inode, offset, options):
    new_target, exist, new_inode = get_tail_filename(filename, False, options)
    if not exist:
        clean_up(inode, f, offset)
        return False

    if target != new_target:
        clean_up(inode, f, offset)

        target = new_target
        inode = new_inode
        offset = get_offset(str(inode))
        f, error = open_tail(target, options, offset)
        if error:
            clean_up(inode, f, 0)
            return False
        options.last_target_filename = target
    return None


class Handler:
    def __init__(self, options):
        self.options = options

    def sig_handler(self, signal, frame):
        if self.options.cat:
            sys.exit(0)

        if self.options.follow_file:
            verbose('Last Open', '{}'.format(self.options.last_target_filename), self.options)
        else:
            path = get_path_of(self.options.last_target_filename)
            verbose('Last Open', '{} in {}'.format(self.options.last_target_filename, path), self.options)

        sys.exit(0)

def print_version():
    print ('{} {}'.format(os.path.basename(sys.argv[0]), program_version))

def get_parser():
    parser = argparse.ArgumentParser(description='tail/cat a log or the newest log in a directory, coloring text. config: colors.json, ver: {}'.format(program_version))

    parser.add_argument('filename', nargs='?', default='.', help='file to process, or directory to process, default: .')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
    parser.add_argument('-f', '--follow', action='store_true', help='follow a file')
    parser.add_argument('-r', '--retry', action='store_true', help='retry on failure')
    parser.add_argument('-N', '--skip-name', action='store_true', help='skip name field when printing log')
    parser.add_argument('-I', '--skip-id', action='store_true', help='skip ID field when printing log')
    parser.add_argument('-D', '--skip-date', action='store_true', help='skip date field when printing log')
    parser.add_argument('-T', '--skip-time', action='store_true', help='skip time field when printing log')
    parser.add_argument('-L', '--skip-level', action='store_true', help='skip level field when printing log')
    parser.add_argument('-S', '--skip-section', action='store_true', help='skip section field when printing log')
    parser.add_argument('-C', '--skip-code', action='store_true', help='skip code field when printing log')
    parser.add_argument('--simple', action='store_true', help='print in simple format, other than original format')
    parser.add_argument('--cat', action='store_true', help='enable cat mode, print log and exit')
    parser.add_argument('--debug', action='store_true', help='enable debug message')
    parser.add_argument('--keyword', action='store_true', help='enable [keyword], (keyword) coloring')
    parser.add_argument('--keyvalue', action='store_true', help='enable key=value coloring')
    parser.add_argument('--version', action='store_true', help='print version information and exit')
    parser.add_argument('--colors-file', type=str, help='use specified colors config file for coloring')

    return parser

def set_options(args, options):
    options.verbose = args.verbose
    options.follow_file = args.follow
    options.retry = args.retry
    options.skip_name = args.skip_name
    options.skip_id = args.skip_id
    options.skip_date = args.skip_date
    options.skip_time = args.skip_time
    options.skip_level = args.skip_level
    options.skip_section = args.skip_section
    options.skip_code = args.skip_code
    options.print_simple_format = args.simple
    options.cat = args.cat
    options.debug = args.debug
    options.keyword_coloring = args.keyword
    options.keyvalue_coloring = args.keyvalue
    options.colors_file = args.colors_file    
    
    if options.colors_file is not None:
        options.colors = True

def load_colors(options):
    config_colors = {}
    if options.colors_file is None:
        filepath = os.path.join(os.path.dirname(__file__), 'colors.json')
    else:
        filepath = options.colors_file
        
    try:
        with open(filepath) as f:
            config_colors = json.load(f)
            verbose('Load Colors', 'from {}'.format(filepath), options)
    except Exception as e:
        verbose('Load Colors, Error', '{} does not exist, {}'.format(filepath, e), options)
        verbose('Colors', 'use default colors', options)
        return
            
    global colors
    set_256_colors()
    
    for key, value in config_colors.items():
        colors[key] = ansi_colors.get(value, '\033[0m')
    
def main():
    parser = get_parser()
    args = parser.parse_args()

    options = Options()
    set_options(args, options)

    if options.colors:
        load_colors(options)

    handler = Handler(options)
    signal.signal(signal.SIGINT, handler.sig_handler)

    if not sys.stdin.isatty():
        cat(options)
        return

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.version:
        print_version()
        return

    filename = args.filename

    if options.cat:
        cat_file(filename, options)
        return

    while True:
        tail(filename, options)
        if options.retry:
            time.sleep(1)
        else:
            break

if __name__ == '__main__':
    main()

