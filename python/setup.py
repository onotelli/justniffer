#!/usr/bin/python 
# -*- coding: utf-8 -*-
#	Copyright (c) 2009 Plecno s.r.l. All Rights Reserved 
#	info@plecno.com
#	via Giovio 8, 20144 Milano, Italy
#	Released under the terms of the GPLv3 or later
#	Author: Oreste Notelli <oreste.notelli@plecno.com>	

import commands
import shutil
import os


e = commands.getstatusoutput
s, p = e ("which justniffer")
if (s == 0):
  scripts_path = p.replace("bin/justniffer", "share/justniffer/scripts")
  try:
    os.makedirs(scripts_path)
  except OSError, ex:
    if (ex.errno ==17):
      pass    
  e ("chmod a+x http_parser.py") 
  shutil.copy("common.py",scripts_path)
  shutil.copy("http_parser.py",scripts_path)
  bin_path = p.replace("bin/justniffer", "bin")
  e ("chmod a+x create_scripts") 
  e ("./create_scripts justniffer-grab-http-traffic.in justniffer-grab-http-traffic " + scripts_path)
  e ("chmod a+x justniffer-grab-http-traffic") 
  shutil.copy("justniffer-grab-http-traffic", bin_path)

  print "INSTALLATION COMPLETED"

