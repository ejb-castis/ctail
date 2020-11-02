#!/usr/bin/env python3
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
    "value": '\033[0;33m',
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
        s = time.strftime('%Y-%m-%d %H:%M:%S',
                          time.gmtime(float(timestamp)+32400))
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
    desc = re.sub("\(([^)]*)\)", "(" + Colors['value'] +
                  r"\1" + Colors['endc'] + ")", desc)
    if _skip_date and _skip_time:
        datetime = ""
    if _skip_level:
        level = ""
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
    if _skip_name:
        name = ""

    id = Colors['id'] + id + Colors['endc']
    if _skip_id:
        id = ""

    date = Colors['date'] + date + Colors['endc']
    if _skip_date:
        date = ""

    time = Colors['time'] + time + Colors['endc']
    if _skip_time:
        time = ""

    if level in ['Error', 'Fail', 'Warning', 'Exception']:
        level = Colors['error'] + level + Colors['endc']
    else:
        level = Colors['level'] + level + Colors['endc']
    if _skip_level:
        level = ""

    section = re.sub("\[([^]]*)\]", "[" + Colors['keyword'] +
                     r"\1" + Colors['endc'] + "]", section)
    section = Colors['section'] + section + Colors['endc']
    if _skip_section:
        section = ""

    code = Colors['code'] + code + Colors['endc']
    if _skip_code:
        code = ""

    description = re.sub("\[([^]]*)\]", "[" + Colors['keyword'] +
                         r"\1" + Colors['endc'] + Colors['description'] + "]", description)
    description = re.sub("\(([^)]*)\)", "(" + Colors['value'] +
                         r"\1" + Colors['endc'] + Colors['description'] + ")", description)
    description = Colors['description'] + description + Colors['endc']

    if _print_simple_format:
        return ','.join([level, date, time, section, code, description]), False

    return ','.join([name, id, date, time, level, section, code, description]), False


def format_ncsacombinedlog(log):
    try:
        host, id, username, datetime, tz, method, uri, version, statuscode, bytes, combined = log.split(
            ' ', 10)
    except Exception as e:
        return log, True
    datetimetz = datetime + " " + tz
    datetimetz = Colors['date'] + datetimetz + Colors['endc']
    request = method + " " + uri + " " + version
    request = Colors['green'] + request + Colors['endc']
    statuscode = Colors['blue'] + statuscode + Colors['endc']
    if _skip_date and _skip_time:
        datetimetz = ""
    return '%s %s %s %s %s %s %s %s' % (host, id, username, datetimetz, request, statuscode, bytes, combined), False


def format_ncsalog(log):
    try:
        host, id, username, datetime, tz, method, uri, version, statuscode, bytes = log.split(
            ' ', 9)
    except Exception as e:
        return log, True
    datetimetz = datetime + " " + tz
    datetimetz = Colors['date'] + datetimetz + Colors['endc']
    request = method + " " + uri + " " + version
    request = Colors['green'] + request + Colors['endc']
    statuscode = Colors['blue'] + statuscode + Colors['endc']
    if _skip_date and _skip_time:
        datetimetz = ""
    return '%s %s %s %s %s %s %s' % (host, id, username, datetimetz, request, statuscode, bytes), False

def format_simplelog(log):
    try:
        level, date, time, section, description = log.split(' ', 4)
    except Exception as e:
        return log, True
    date = Colors['date'] + date + Colors['endc']
    if _skip_date:
        date = ""

    time = Colors['time'] + time + Colors['endc']
    if _skip_time:
        time = ""

    if level in ['Error', 'Fail', 'Warning', 'Exception', 'ERROR', 'FAIL']:
        level = Colors['error'] + level + Colors['endc']
    else:
        level = Colors['level'] + level + Colors['endc']
    if _skip_level:
        level = ""

    section = re.sub("\[([^]]*)\]", "[" + Colors['keyword'] +
                     r"\1" + Colors['endc'] + "]", section)
    section = Colors['section'] + section + Colors['endc']
    if _skip_section:
        section = ""

    description = re.sub("\[([^]]*)\]", "[" + Colors['keyword'] +
                         r"\1" + Colors['endc'] + Colors['description'] + "]", description)
    description = re.sub("\(([^)]*)\)", "(" + Colors['value'] +
                         r"\1" + Colors['endc'] + Colors['description'] + ")", description)
    description = Colors['description'] + description + Colors['endc']

    return ' '.join([level, date, time, section, description]), False

def print_format_log(log):
    if log.startswith('0x'):
        log, error = format_eventlog(translate(log))
    else:
        log, error = format_cilog(log)
        if error:
          log, error = format_simplelog(log)
          if error:
            log, error = format_ncsacombinedlog(log)
            if error:
              log, error = format_ncsalog(log)
    print(log, end=' ')

def is_binary(filename):
    """Return true if the given filename is binary.
    @raise EnvironmentError: if the file does not exist or cannot be accessed.
    @attention: found @ http://bytes.com/topic/python/answers/21222-determine-file-type-binary-text on 6/08/2010
    @author: Trent Mick <TrentM@ActiveState.com>
    @author: Jorge Orpinel <jorge@orpinel.com>"""
    with open(filename, 'rb') as f:
      CHUNKSIZE = 1024
      while 1:
          chunk = f.read(CHUNKSIZE)
          if b'\0' in chunk:  # found null byte
              return True
          if len(chunk) < CHUNKSIZE:
              break  # done
    return False

def newest_file_in(path):
    def mtime(f): return os.stat(os.path.join(path, f)).st_mtime
    ls = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if len(ls) == 0:
        return ""

    newest_file_name = ""
    soreted_ls = list(sorted(ls, key=mtime))
    while (len(soreted_ls) > 0):
        f = soreted_ls.pop()
        if is_binary(os.path.join(path, f)) == False:
            newest_file_name = f
            break
    if newest_file_name == "":
        return ""
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
    for line in fileinput.input("-"):
        print_format_log(line)
        sys.stdout.softspace = 0


def open_head(filename, offset):
    global _last_target_filename
    try:
        f = open(filename)
        if _verbose and _last_target_filename != filename:
          if _follow_file:
            print(colorize_ok('>>> Open :%s' % filename), end=' ')
            print(colorize_ok(", offset :{:,}".format(offset)))
          else:
            path = get_path_of(filename)
            print(colorize_ok(">>> Open :{} in {}".format(filename,path)), end=' ')
            print(colorize_ok(", offset :{:,}".format(offset)))

        f.seek(offset, 0)
    except Exception as e:
        if _verbose:
            print(colorize_ok('>>> Error :%s' % filename), end=' ')
            print(e)
        return None, True

    _last_target_filename = filename
    return f, False


def open_tail(filename):
    global _last_target_filename

    try:
        f = open(filename)
        size = os.path.getsize(filename)

        if _verbose and _last_target_filename != filename:
          if _follow_file:
            print(colorize_ok('>>> Open :%s' % filename), end=' ')
            print(colorize_ok(", size :{:,}".format(size)))
          else:
            path = get_path_of(filename)
            print(colorize_ok("\n>>> Open :{} in {}".format(filename,path)), end=' ')
            print(colorize_ok(", size :{:,}".format(size)))

        if size >= 2048:
          f.seek(size - 2048, 0)

        line = f.readline()
    except Exception as e:
        if _verbose:
            print(colorize_ok('>>> Error :%s' % filename), end=' ')
            print(e)
        return None, True

    _last_target_filename = filename
    return f, False


def get_tail_filename(filename, follow_file):
    if follow_file:
        if not exist_file(filename):
            if _verbose:
                print(colorize_ok('>>> Not found :%s' % filename))
            return None, False
        if is_binary(filename):
            if _verbose:
                print(colorize_ok('>>> Not a text file :%s' % filename))
            return None, False

        tail_file = filename
    else:
        try:
            path = get_path_of(filename)
            if not exist_directory(path):
                if _verbose:
                    print(colorize_ok('>>> Not found path :%s' % path))
                return None, False
            tail_file = newest_file_in(path)
            if tail_file == "":
                print(colorize_ok('>>> Error : No text files in %s' % path))
                return None, False
        except Exception as e:
            if _verbose:
                print(colorize_ok('>>> Error :%s' % path), end=' ')
                print(e)
            return None, False
    return tail_file, True


def keep_tail(f):
    while True:
        try:
            line = f.readline()
        except Exception as e:
            if _verbose:
                print(colorize_ok('>>> Error :' % e))
            f.close()
            return 0, True
        if line:
            print_format_log(line)
            sys.stdout.softspace = 0
        else:
            break
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
    if not exist:
        return None, None, None, True

    if target_filename == re_target_filename:
        try:
            new_target_filename_offset = os.path.getsize(target_filename)
        except Exception as e:
            if _verbose:
                print(colorize_ok('>>> Error :%s' % target_filename), end=' ')
                print(e)
            return None, None, None, True

        if target_file_offset <= new_target_filename_offset:
            f, error = open_head(target_filename, target_file_offset)
            if error:
                return None, None, None, True
        else:
            f, error = open_head(target_filename, 0)
            if error:
                return None, None, None, True

    else:
        target_filename = re_target_filename
        target_file_offset, exist = get_offset(target_filename)
        f, error = open_head(target_filename, target_file_offset)
        if error:
            return None, None, None, True

    return f, target_filename, target_file_offset, False


def tail(filename, follow_file):
    target, exist = get_tail_filename(filename, follow_file)
    if not exist:
        return

    if _last_target_filename == '':
        f, error = open_tail(target)
        if error:
            return
    else:
        target = _last_target_filename
        offset, exist = get_offset(target)
        f, target, offset, error = reopen_tail(
            filename, follow_file, target, offset)
        if error:
            return

    while True:
        offset, error = keep_tail(f)
        if error:
            return

        put_offset(target, offset)

        f, target, offset, error = reopen_tail(
            filename, follow_file, target, offset)
        if error:
            return

        time.sleep(0.01)


def sig_handler(signal, frame):
    if _verbose:
        offset, exist = get_offset(_last_target_filename)
        print(colorize_ok("\n>>> Open files :%s" % _fileoffset_repository), end=' ')
        if _follow_file:
          print(colorize_ok("\n>>> Last Open :%s" % _last_target_filename), end=' ')
          print(colorize_ok(", offset :{:,}".format(offset)))
        else:
          path = get_path_of(_last_target_filename)
          print(colorize_ok("\n>>> Last Open :{} in {}".format(_last_target_filename,path)), end=' ')
          print(colorize_ok(", offset :{:,}".format(offset)))

    sys.exit(0)


def usage():
    print(os.path.basename(sys.argv[0]) + ' ' + _version)
    print('Usage: %s [option] FILE' % os.path.basename(sys.argv[0]))
    print(' or :  %s [option] DIRECTORY' % os.path.basename(sys.argv[0]))
    print('')
    print('Continuosly tail the newest text file in DIRECTORY(or in the directory of FILE)')
    print('or tail the specific FILE with -f option')
    print('Options:')
    print('--version      print version')
    print('-f             follow FILE, not to tail the newest file in the directory of FILE')
    print('-r, --retry    keep trying to open a file if it is inaccessible. sleep for 1.0 sec between retry iterations')
    print('-v, --verbose  print messages verbosely')
    print('--simple       to print simple format')
    print('-N             not to print name field of cilog')
    print('-I             not to print id field of cilog')
    print('-D             not to print date field of cilog')
    print('-T             not to print time field of cilog')
    print('-L             not to print level field of cilog')
    print('-S             not to print section field of cilog')
    print('-C             not to print code field of cilog')


def print_version():
    print(_version)


def main():
    global _version
    _version = "0.1.8"

    global _skip_name
    _skip_name = False

    global _skip_id
    _skip_id = False

    global _skip_date
    _skip_date = False

    global _skip_time
    _skip_time = False

    global _skip_level
    _skip_level = False

    global _skip_section
    _skip_section = False

    global _skip_code
    _skip_code = False

    global _print_simple_format
    _print_simple_format = False

    signal.signal(signal.SIGINT, sig_handler)

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

    global _follow_file
    _follow_file = False
    retry = False

    try:
        options, args = getopt.getopt(sys.argv[1:], "vfhrNIDTLSC", [
            "simple", "help", "retry", "version", "verbose"])
    except getopt.GetoptError as err:
        print(str(err))
        print("")
        usage()
        sys.exit(1)

    for op, p in options:
        if op == "--version":
            print_version()
            sys.exit(1)
        if op == "-v" or op == "--verbose":
            _verbose = True
        if op == "-f":
            _follow_file = True
        if op == "-r" or op == "--retry":
            retry = True
        if op == "-h" or op == "--help":
            usage()
            sys.exit(1)
        if op == "-N":
            _skip_name = True
        if op == "-I":
            _skip_id = True
        if op == "-D":
            _skip_date = True
        if op == "-T":
            _skip_time = True
        if op == "-L":
            _skip_level = True
        if op == "-S":
            _skip_section = True
        if op == "-C":
            _skip_code = True
        if op == "--simple":
            _print_simple_format = True

    if not sys.stdin.isatty():
        cat()
        return

    if len(args) > 0:
        filename = args[0]

    while True:
        tail(filename, _follow_file)
        if retry:
            time.sleep(1)
        else:
            break


if __name__ == '__main__':
    main()
