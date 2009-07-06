#!/usr/bin/python
# -*- coding: utf-8 -*-
#	Copyright (c) 2009 Plecno s.r.l. All Rights Reserved 
#	info@plecno.com
#	via Giovio 8, 20144 Milano, Italy
#	Released under the terms of the GPLv3 or later
#	Author: Oreste Notelli <oreste.notelli@plecno.com>	

import SimpleHTTPServer
import BaseHTTPServer
import os
import cgi
import urlparse
import json
import datetime
import baseweb
import shutil


content_type = baseweb.content_type
document_root = "./" 

class myEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Exception):
      return str((obj, dir(obj))) 
    return str(obj)
    #return json.JSONEncoder.default(self, obj)

def to_json(val):
  return json.dumps(val, cls=myEncoder)

def get_arguments(querystring):
  parsed_query = cgi.parse_qs(querystring)
  kargs = dict()
  args = dict()
  for k, v in parsed_query.items():
    if (len (v) > 1):
      value=v
    else:
      value=v[0]
    try:
      ik = int(k)
      args[ik] = value
    except:
      kargs[k] = value
  newargs = list()
  for e in sorted(args):
    newargs.append(args[e])
  return newargs, kargs

def get_function(path):
  parts = path.strip("/").split("/")
  module_name = ""
  for module in parts[:-1] :
    if len(module_name) > 0:
      module_name += "."
    module_name += module
    m = __import__(module_name)
  function_name = parts[-1]
  f = m.__dict__[function_name]
  retf = f
  if not isinstance (f, baseweb.cache):
    retf = baseweb.cache(f)
    m.__dict__[function_name] = retf
    
  return retf
  #return f

def format_error(exception):
  return "(error="+ to_json(exception)+")"

    

class MyHTTPRequestHandler (SimpleHTTPServer.SimpleHTTPRequestHandler):
  base = SimpleHTTPServer.SimpleHTTPRequestHandler
  def __init__(self, *args, **kargs):
    return SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kargs)
  def do_GET(self):
    path = self.translate_path(self.path)
    if (os.path.exists(path)):
      MyHTTPRequestHandler.base.do_GET(self)
    else:
      content = ""
      try:
	self.execute()
      except Exception, e:
	self.send_response(500)
	content= format_error(e)
	self.write_string(content)

  def execute (self):
    r = urlparse.urlparse(self.path)
    f = get_function(r.path)
    args, kargs = get_arguments(r.query)
    res = f(*args, **kargs)
    self.send_response(200)
    if isinstance(res, baseweb.content_type):
      self.send_header('Content-type',res.get_content_type())
      self.send_header('Content-length', res.get_content_length() )
      self.end_headers()
      shutil.copyfileobj(res.get_content(), self.wfile)
      self.wfile.close()
    else:
      content =  "(result="+to_json (f(*args, **kargs))+")"
      self.write_string(content)
      self.send_header('Content-type','text/plain')
	
  def write_string(self, content):
      self.send_header('Content-type','text/plain')
      self.send_header('Content-length', len (content) )
      self.end_headers()
      self.wfile.write(content)
      self.wfile.close()


def MyFactory(root):
  def _Factory(*args, **kargs):
    h = MyHTTPRequestHandler(*args, **kargs)
    setattr(h, "root", root)
    return h
  return _Factory

PORT = 8080


httpd = BaseHTTPServer.HTTPServer(("", PORT), MyFactory(document_root))

print "serving at port", PORT
httpd.serve_forever()

