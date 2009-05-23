#!/usr/bin/python 
# -*- coding: utf-8 -*-
import subprocess
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory",
                  help="MANDATORY: directory where to save files")
parser.add_option("-p", "--packet-filter", dest="packet_filter",
                  help="packet filter (tcpdump filter syntax)", default="\"port 80\"")
parser.add_option("-U", "--user", dest="user",
                  help="user to impersonate when saving files")
parser.add_option("-i", "--interface", dest="interface",
                  help="network interface to listen on (e.g. eth0, en1, etc.)")
parser.add_option("-f", "--filecap", dest="filecap",
                  help="input file in 'tcpdump capture file format'")

(options, args) = parser.parse_args()

if (options.directory == None):
  parser.print_help()
  sys.exit(-1)

options_to_pass=list()

def check(opt, str_opt, options_to_pass):
  if (opt):
    options_to_pass.append(str_opt)
    options_to_pass.append(opt)
  
check(options.user, "-U", options_to_pass)
check(options.interface, "-i", options_to_pass)
check(options.filecap, "-f", options_to_pass)
check(options.packet_filter, "-p", options_to_pass)
options_to_pass.append("-r")
options_to_pass.append("-e")
options_to_pass.append('"./http_parser.py -d "'+ '"'+options.directory+'"')
options_to_pass.insert(0, "justniffer")
result = subprocess.call(options_to_pass)

