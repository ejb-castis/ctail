#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014. 06. 09
@author: <mwpark@castis.com>
'''
import signal
import time
import os
import sys
import re
import fileinput
import getopt

Colors = {
    "name": '\033[0m',
    "id": '\033[0m',
    "date": '\033[1;34m',
    "time": '\033[1;36m',
    "level": '\033[0;38;05;81m',
    "section": '\033[0m',
    "code": '\033[0;32m',
    "description": '\033[0;38;05;187m',
    "error": '\033[0;38;05;161m',
    "ok": '\033[0;38;05;118m',
    "number": '\033[0;38;05;141m',
    "keyword": '\033[0;38;05;208m',
    "variable": '\033[0;38;05;187m',
    "value": '\033[0;38;05;208m',
    "blue":     '\033[0;38;05;081m',
    "pink":     '\033[1;38;05;161m',
    "pinkbold": '\033[1;38;05;161m',
    "orange":   '\033[0;38;05;208m',
    "green":    '\033[0;38;05;118m',
    "purple":   '\033[0;38;05;141m',
    "string":   '\033[0;92m',
    "endc":     '\033[0m'}

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
        return s
    except Exception as e:
        return ''

def translate(log):
    try:
        event, level, datetime, desc = log.split(',', 3)
    except Exception as e:
        return log
    event = get_event_type_string(event)
    level = get_event_level_string(level)
    datetime = get_time_string_gmt_to_kst(datetime)
    return ','.join([event, level, datetime, desc])

def format_eventlog(log):
    try:
        event, level, datetime, desc = log.split(',', 3)
    except Exception as e:
        return log, True
    if level in ['error', 'fail', 'warning', 'except']:
        level = Colors['pinkbold'] + level + Colors['endc']
    else:
        level = Colors['blue'] + level + Colors['endc']
    event = Colors['green'] + event + Colors['endc']
    desc = re.sub("\[([^](]*)\]", "[" + Colors['keyword'] +
                  r"\1" + Colors['endc'] + "]", desc)
    desc = re.sub("\(([^)]*)\)", "(" + Colors['purple'] +
                  r"\1" + Colors['endc'] + ")" , desc)
    return '%s %s %s %s' % (datetime, event, level, desc), False

def colorize_ok(str):
    return Colors['ok'] + str + Colors['endc']

def format_cilog(log):
    try:
        name, id, date, time, level, section, code, description = log.split(
            ',', 7)
    except Exception as e:
        return log, True
    name = Colors['name'] + name + Colors['endc']
    id = Colors['id'] + id + Colors['endc']
    date = Colors['date'] + date + Colors['endc']
    time = Colors['time'] + time + Colors['endc']
    if level in ['Error', 'Fail', 'Warning']:
        level = Colors['error'] + level + Colors['endc']
    else:
        level = Colors['level'] + level + Colors['endc']
    section = re.sub("\[([^]]*)\]", "[" + Colors['keyword'] +
                     r"\1" + Colors['endc'] + "]", section)
    section = Colors['section'] + section + Colors['endc']
    code = Colors['code'] + code + Colors['endc']
    description = re.sub("\[([^]]*)\]", "[" + Colors['keyword'] +
                         r"\1" + Colors['endc'] + Colors['description'] + "]", description)
    description = re.sub("\(([^)]*)\)", "(" + Colors['purple'] +
                         r"\1" + Colors['endc'] + Colors['description'] + ")", description)
    description = Colors['description'] + description + Colors['endc']
    return ','.join([name, id, date, time, level, section, code, description]), False

def print_format_log(log):
    if log.startswith('0x'):
        log, error = format_eventlog(translate(log))
    else:
        log, error = format_cilog(log)
    print log,

def newest_file_in(path):
    def mtime(f): return os.stat(os.path.join(path, f)).st_mtime
    ls = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    newest_file_name = list(sorted(ls, key=mtime))[-1]
    return os.path.join(path, newest_file_name)

def get_path_of(filename):
    path = os.path.realpath(filename)
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    return path

def exist_file(filename):
    return os.path.isfile(filename) or os.path.islink(filename)

def exist_directory(directory):
    return os.path.exists(directory)

def cat():
    for line in fileinput.input():
        print_format_log(line)
        sys.stdout.softspace = 0

def open_head(filename, offset):
    global _last_target_filename
    try:
        f = open(filename)
        if _verbose and _last_target_filename != filename: 
            print colorize_ok('>>> Open :%s' % filename),
            print ", offset:" , offset
        f.seek(offset, 0)
    except Exception as e:
        if _verbose:
            print colorize_ok('>>> Error :%s' % filename),
            print e
        f.close()
        return None, True

    _last_target_filename = filename
    return f, False

def open_tail(filename):
    global _last_target_filename

    try:
        f = open(filename)
        size = os.path.getsize(filename)

        if _verbose and _last_target_filename != filename: 
            print colorize_ok('>>> Open :%s' % filename),
            print colorize_ok(', size :%s' % size)

        if size >= 2048: 
            f.seek(-2048, 2)
            line = f.readline()                         
    except Exception as e:
        if _verbose:
            print colorize_ok('>>> Error :%s' % filename),
            print e
        f.close()
        return None, True

    _last_target_filename = filename
    return f, False

def get_tail_filename(filename, follow_file):
    
    if follow_file:
        if not exist_file(filename): 
            if _verbose: print colorize_ok('>>> Not found :%s' % filename)
            return None, False
        tail_file = filename
    else:
        try:
            path = get_path_of(filename)
            if not exist_directory(path):
              if _verbose: print colorize_ok('>>> Not found path :%s' % path)
              return None, False
            tail_file = newest_file_in(path)
        except Exception as e:
            if _verbose:
                print colorize_ok('>>> Error :%s' % path),
                print e
            return None, False   
    return tail_file, True

def keep_tail(f):
    while True:
        try:
            line = f.readline()
        except Exception as e:
            if _verbose: print colorize_ok('>>> Error :' % e)
            f.close()
            return 0, True
        if line: 
            print_format_log(line)
            sys.stdout.softspace=0
        else: break
    offset = f.tell()
    f.close()
    return offset, False

def put_offset(filename, offset):
    global _fileoffset_repository
    _fileoffset_repository[filename] = offset

def get_offset(filename):
    global _fileoffset_repository
    try:
        offset = _fileoffset_repository[filename]
        return offset, True
    except Exception as e:
        return 0, False

def reopen_tail(filename, follow_file, target_filename, target_file_offset):
    re_target_filename, exist = get_tail_filename(filename, follow_file)
    if not exist: return None, None, None, True
    
    if target_filename == re_target_filename:
        try:
            new_target_filename_offset = os.path.getsize(target_filename)
        except Exception as e:
            if _verbose:
                print colorize_ok('>>> Error :%s' % target_filename),
                print e
            return None, None, None, True

        if  target_file_offset <= new_target_filename_offset:
            f, error = open_head(target_filename, target_file_offset)
            if error: return None, None, None, True
        else:
            f, error = open_head(target_filename, 0)
            if error: return None, None, None, True

    else:
        target_filename = re_target_filename
        target_file_offset, exist = get_offset(target_filename)
        f, error = open_head(target_filename, target_file_offset)
        if error: return None, None, None, True

    return f, target_filename, target_file_offset, False

def tail(filename, follow_file):
    target, exist = get_tail_filename(filename, follow_file)
    if not exist: return

    if _last_target_filename == '':
        f, error = open_tail(target)
        if error: return
    else:
        target = _last_target_filename
        offset, exist = get_offset(target)
        f, target, offset, error = reopen_tail(filename, follow_file, target, offset)
        if error: return

    while True:
        offset, error = keep_tail(f)
        if error: return

        put_offset(target, offset)

        f, target, offset, error = reopen_tail(filename, follow_file, target, offset)
        if error : return
               
        time.sleep(0.01)

def sig_handler(signal, frame):
    if _verbose: 
        offset, exist = get_offset(_last_target_filename)
        print colorize_ok("\n>>> Open files :%s" % _fileoffset_repository),
        print colorize_ok("\n>>> Last Open :%s" % _last_target_filename), 
        print colorize_ok(", offset :%s" % offset)
    sys.exit(0)

def usage():
    print 'Usage: %s [option] FILE' % os.path.basename(sys.argv[0])
    print ' or :  %s [option] DIRECTORY' % os.path.basename(sys.argv[0])
    print ''
    print 'Continuosly tail the newest file in DIRECTORY(or in the directory of FILE)'
    print 'or tail the specific FILE with -f option'
    print 'Options:'
    print '--version      print version'
    print '-f             follow FILE, not to tail the newest file in the directory of FILE'
    print '-r, --retry    keep trying to open a file if it is inaccessible. sleep for 1.0 sec between retry iterations'
    print '-v, --verbose  print messages verbosely'

def print_version():
    print '0.1.2'

def main():
    signal.signal(signal.SIGINT, sig_handler)
    if len(sys.argv) == 1 and not sys.stdin.isatty():
        cat()
        return

    if len(sys.argv) < 2 and sys.stdin.isatty():
        usage()
        sys.exit(1)

    global _verbose
    _verbose = False

    global _fileoffset_repository
    _fileoffset_repository = {}

    global _last_target_filename
    _last_target_filename = ""

    filename = '.'
    follow_file = False
    retry = False

    try:
        options, args = getopt.getopt(sys.argv[1:], "vfhr", ["help", "retry", "version", "verbose"])
    except getopt.GetoptError as err:
        print str(err)
        print ""
        usage()
        sys.exit(1)

    for op, p in options:
        if op == "--version":
            print_version()
            sys.exit(1)
        if op == "-v" or op == "--verbose":
            _verbose = True
        if op == "-f":
            follow_file = True
        if op == "-r" or op == "--retry":
            retry = True
        if op == "-h" or op == "--help":
            usage()
            sys.exit(1)

    if len(args) > 0:
        filename = args[0]

    while True:
        tail(filename, follow_file)
        if retry:
            time.sleep(1)
        else: 
            break

if __name__ == '__main__':
    main()
