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

Colors = {
		"name": '\033[0m',
		"id": '\033[0m',
		"date": '\033[0m',
		"time": '\033[0m',
		"level": '\033[38;5;150m',
		"section": '\033[0m',
		"code": '\033[0m',
		"description": '\033[38;5;187m',
		"error": '\033[38;5;197m',
		"ok": '\033[38;5;35m',
		"number": '\033[38;5;179m',
		"endc": '\033[0m'}

def colorize_ok(str):
	return Colors['ok'] + str + Colors['endc']

def colorize_log(log):
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
	section = Colors['section'] + section
	code = Colors['code'] + code
	description = re.sub("\(([^)]*)\)", "(" + Colors['number'] + r"\1" + Colors['description'] + ")", description)
	description = re.sub("\[([^]]*)\]", "[" + Colors['number'] + r"\1" + Colors['description'] + "]", description)
	description = Colors['description'] + description + Colors['endc']
	return ','.join([name, id, date, time, level, section, code, description])

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

def tail(filename):
	path = get_path_of(filename)
	current_file = newest_file_in(path)
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
			print colorize_log(line),
		else:
			last_file = newest_file_in(path)
			if not current_file == last_file:
				current_file = last_file
				f.close()
				f = open(os.path.join(path, current_file))
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
	if len(sys.argv) != 2:
		usage()
		sys.exit(1)
	signal.signal(signal.SIGINT, sig_handler)
	tail(sys.argv[1])
