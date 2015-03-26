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

Colors = {
        "name": '\033[0m',
        "id": '\033[0m',
        "date": '\033[0m',
        "time": '\033[0m',
        "level": '\033[0;38;05;81m',
        "section": '\033[0m',
        "code": '\033[0m',
        "description": '\033[0;38;05;187m',
        "error": '\033[0;38;05;161m',
        "ok": '\033[0;38;05;118m',
        "number": '\033[0;38;05;141m',
        "keyword": '\033[0;38;05;208m',
        "blue":     '\033[0;38;05;081m',
        "pink":     '\033[1;38;05;161m',
        "pinkbold": '\033[1;38;05;161m',
        "orange":   '\033[0;38;05;208m',
        "green":    '\033[0;38;05;118m',
        "purple":   '\033[0;38;05;141m',
        "string":   '\033[0;38;05;222m',
        "endc":     '\033[0m'}

event_type_major  = {
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
        s = event_type_major[int(event, 0)&0xFFFF0000]
        if s == 'SU':
            s = s + '/' + session_event_type[int(event, 0)&0xFFFF]
        return s
    except:
        return ''


def get_event_level_string(level):
    return event_level[int(level)]


def get_time_string_gmt_to_kst(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(timestamp)+32400))


def translate(log):
    try:
        event, level, datetime, desc = log.split(',', 3)
    except:
        return log
    event = get_event_type_string(event)
    level = get_event_level_string(level)
    datetime = get_time_string_gmt_to_kst(datetime)
    return ','.join([event, level, datetime, desc])


def format_eventlog(log):
    try:
        event, level, datetime, desc = log.split(',', 3)
    except:
        return log
    if level in ['error', 'fail', 'warning', 'except']:
        level = Colors['pinkbold'] + level + Colors['endc']
    else:
        level = Colors['blue'] + level + Colors['endc']
    event = Colors['green'] + event + Colors['endc']
    desc = re.sub("(\[[^](]+\])", Colors['string'] + r"\1" + Colors['endc'] , desc)
    desc = re.sub("(\([^)]+\))", Colors['purple'] + r"\1" + Colors['endc'] , desc)
    return '%s %s %s %s' % (datetime, event, level, desc)


def colorize_ok(str):
    return Colors['ok'] + str + Colors['endc']


def format_cilog(log):
    try:
        name, id, date, time, level, section, code, description = log.split(',', 7)
    except:
        return log
    name = Colors['name'] + name
    id = Colors['id'] + id
    date = Colors['date'] + date
    time = Colors['time'] + time
    if level in ['Error', 'Fail', 'Warning']:
        level = Colors['error'] + level
    else:
        level = Colors['level'] + level
    section = re.sub("\[([^]]*)\]", "[" + Colors['keyword'] + r"\1" + Colors['section'] + "]", section)
    section = Colors['section'] + section
    code = Colors['code'] + code
    description = re.sub("\[([^]]*)\]", "[" + Colors['keyword'] + r"\1" + Colors['description'] + "]", description)
    description = re.sub("\(([^)]*)\)", "(" + Colors['keyword'] + r"\1" + Colors['description'] + ")", description)
    description = Colors['description'] + description + Colors['endc']
    return ','.join([name, id, date, time, level, section, code, description])


def print_format_log(log):
    if log.startswith('0x'):
        print format_eventlog(translate(log)),
    else:
        print format_cilog(log),


def newest_file_in(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    ls = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    newest_file_name = list(sorted(ls, key=mtime))[-1]
    return os.path.join(path, newest_file_name)


def get_path_of(filename):
    path = os.path.realpath(filename)
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    return path


def cat():
    for line in fileinput.input():
        print_format_log(line)
        sys.stdout.softspace=0


def tail(filename):
    path = get_path_of(filename)
    try:
        current_file = newest_file_in(path)
    except:
        print "cannot file files in", path
        usage()
        return

    f = open(current_file)
    print colorize_ok('>>> open %s' % current_file)
    try:
        f.seek(-2048, 2)
        f.readline()
    except:
        pass
    while True:
        line = f.readline()
        if line:
            print_format_log(line)
            sys.stdout.softspace=0
        else:
            last_file = newest_file_in(path)
            if not current_file == last_file:
                current_file = last_file
                f.close()
                f = open(os.path.join(path, current_file))
                if "EventLog" in current_file:
                    log_type = "eventlog"
                else:
                    log_type = "cilog"
                print colorize_ok('>>> open %s' % current_file)
            time.sleep(0.1)


def sig_handler(signal, frame):
    sys.exit(0)


def usage():
    print 'Usage: %s FILE' % os.path.basename(sys.argv[0])
    print ' or :  %s DIRECTORY' % os.path.basename(sys.argv[0])
    print 'Continuosly tail last file in DIRECTORY(or the directory of FILE).'
    print 'Report bugs to <mwpark@castis.com>'


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sig_handler)
    if len(sys.argv) != 2 and sys.stdin.isatty():
        usage()
        sys.exit(1)

    if len(sys.argv) == 1 and not sys.stdin.isatty():
        cat()
    else:
        tail(sys.argv[1])
