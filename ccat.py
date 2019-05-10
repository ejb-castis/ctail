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
import datetime
from dateutil.parser import parse

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
    global _begin_time, _end_time
    try:
        event, level, datetime, desc = log.split(',', 3)

        logtime, error = convert_datetime(datetime, False)
        if error: pass
        else : 
          if _begin_time : 
            if _begin_time <= logtime : pass
            else : return '', False
          if _end_time : 
            if logtime < _end_time : pass
            else : return '', False

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
                  r"\1" + Colors['endc'] + ")" , desc)
    return '%s %s %s %s' % (datetime, event, level, desc), False

def colorize_ok(str):
    return Colors['ok'] + str + Colors['endc']

def format_cilog(log):
    try:
        name, id, date, time, level, section, code, description = log.split(
            ',', 7)

        logtime, error = convert_datetime(date + "T" + time, False)
        if error: pass
        else : 
          if _begin_time : 
            if _begin_time <= logtime : pass
            else : return '', False
          if _end_time : 
            if logtime < _end_time : pass
            else : return '', False

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
    description = re.sub("\(([^)]*)\)", "(" + Colors['value'] +
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

def open_ccat(filename):
    global _last_target_filename
    global _begin_time, _end_time
    try:
        f = open(filename)
        size = os.path.getsize(filename)
        if _verbose and _last_target_filename != filename: 
            print colorize_ok('>>> Open :%s' % filename),
            if _begin_time or _end_time: print colorize_ok(', size :%s' % size),
            else : print colorize_ok(', size :%s' % size)
            print_time()
    except Exception as e:
        if _verbose:
            print colorize_ok('>>> Error :%s' % filename),
            print e
        return None, True
    _last_target_filename = filename
    return f, False

def get_target_filename(filename, follow_file):
    if follow_file:
        if not exist_file(filename): 
            if _verbose: print colorize_ok('>>> Not found :%s' % filename)
            return None, False
        target_file = filename
    else:
        try:
            path = get_path_of(filename)
            if not exist_directory(path):
              if _verbose: print colorize_ok('>>> Not found path :%s' % path)
              return None, False
            target_file = newest_file_in(path)
        except Exception as e:
            if _verbose:
                print colorize_ok('>>> Error :%s' % path),
                print e
            return None, False   
    return target_file, True

def ccat_lines(f):    
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

def print_time():
    global _begin_time, _end_time
    if _begin_time or _end_time:
      print colorize_ok(">>>"),
      if _begin_time and _end_time: 
        print colorize_ok("begin time :%s" % _begin_time), 
        print colorize_ok(", end time :%s" % _end_time)
      elif _begin_time: print colorize_ok("begin time :%s" % _begin_time)
      elif _end_time : print colorize_ok("end time :%s" % _end_time)

def print_last_open_files():
    global _filenames, _fileoffset_repository, _last_target_filename
    if _verbose or _verboseLast:
        print colorize_ok(">>> Open files :%s" % _filenames)
        print colorize_ok(">>> Actural Open files :{"),
        actualfiles = []
        actualfile_offsets = []
        for fn in _filenames:
          offset, exist = get_offset(fn)
          if exist : 
            actualfiles.append(fn)
            actualfile_offsets.append(offset)
        for i, afn in enumerate(actualfiles):
          if i == len(actualfiles)-1 :
            print colorize_ok("'%s': %d" % (afn, actualfile_offsets[i])) ,
          else: print colorize_ok("'%s': %d," % (afn, actualfile_offsets[i])),
        print colorize_ok("}"),
        offset, exist = get_offset(_last_target_filename)
        print colorize_ok("\n>>> Last Open :%s" % _last_target_filename), 
        print colorize_ok(", offset :%s" % offset)
        print_time()

def ccat(filename, follow_file):
    target, exist = get_target_filename(filename, follow_file)
    if not exist: return

    f, error = open_ccat(target)
    if error: return

    offset, error = ccat_lines(f)
    if error: return
    put_offset(target, offset)

def sig_handler(signal, frame):
    print_last_open_files()
    sys.exit(0)

def usage():
    print 'Usage: %s [option] FILE' % os.path.basename(sys.argv[0])
    print ''
    print 'Catenates file or files'
    print 'Options:'
    print '-b             specify log begin datetime : ex) 2019-05-10T12:00:00'
    print '-e             specify log end datetime : ex) 2019-05-10T13:10:00'
    print '--version      print version'
    print '-v, --verbose  print messages verbosely'
    print '-V,            print last message only'

def print_version():
    print '0.1.0'

def convert_datetime(dt, print_error):
  try:
    d_t = parse(dt)
  except Exception as e:
    if print_error:
      print colorize_ok('>>> Error : datetime option'),
      print colorize_ok(str(e))
    return None, True
  return d_t, False

def main():
    global _begin_time, _end_time
    _begin_time = ''
    _end_time= ''

    signal.signal(signal.SIGINT, sig_handler)
    if len(sys.argv) == 1 and not sys.stdin.isatty():
        cat()
        return
    if len(sys.argv) < 2 and sys.stdin.isatty():
        usage()
        sys.exit(1)

    global _verbose, _verboseLast
    _verbose = False
    _verboseLast = False

    global _fileoffset_repository
    _fileoffset_repository = {}

    global _last_target_filename
    _last_target_filename = ""

    global _filenames
    follow_file = True
    bd=''
    ed=''   
  
    try:
        options, args = getopt.getopt(sys.argv[1:], "Vvhb:e:", ["help", "version", "verbose"])
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
        if op == "-V":
            _verboseLast = True            
        if op == "-b":
            bd = p
        if op == "-e":
            ed = p
        if op == "-h" or op == "--help":
            usage()
            sys.exit(1)

    error = False
    if bd : _begin_time, error = convert_datetime(bd, True)
    if error : sys.exit(1)
    if ed : _end_time, error = convert_datetime(ed, True)
    if error : sys.exit(1)
    if _begin_time and _end_time : 
      if _begin_time >= _end_time :
        print colorize_ok('>>> Error : datetime option : should be begin time < end time'),
        sys.exit(1)

    if len(args) > 0:
        _filenames = args
        if _verbose:
          print colorize_ok(">>> Open files :%s" % _filenames)
          print_time()

    else:
        usage()
        sys.exit(1)

    for filename in _filenames:
      ccat(filename, follow_file)

    print_last_open_files()      

if __name__ == '__main__':
    main()
