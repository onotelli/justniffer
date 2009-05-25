#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: 
# 1 - moving the setuid to the justniffer process
# 2 - when creating directories or files the structure must me rebuild
#    example: 
#  	il /tmp/navigation/www.lastampa.it/commons/test.gif is a file
# 	and /tmp/navigation/www.lastampa.it/commons/test.gif?a=b/index.gif
#	must be created , /tmp/navigation/www.lastampa.it/commons/test.gif 
#	should be deleted
# 3 - does not work with pipelined GET

import httplib
import sys
import commands
import os
import gzip
import StringIO
import mimetypes
import pwd
import shutil
from optparse import OptionParser


parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory",
                  help="Directory where to save files")
parser.add_option("-u", "--user", dest="user", 
                  help="the user that will be set when running the script")

(options, args) = parser.parse_args()

if ((options.user == None) or (options.directory == None)):
  parser.print_help()
  sys.exit(-1)

user=options.user
directory=options.directory

def uid_from_username(username):
  return pwd.getpwnam(username)[2]

os.setuid(uid_from_username(user))

e = commands.getoutput

reponse = httplib.HTTPResponse

class fakesocket:
  def __init__(self, stream):
    self.__stream = stream
  def makefile(self, *args):
    return self.__stream

def recursive_mkdir(path):
  cmd = "mkdir -p \""+path+"\""
  commands.getstatusoutput(cmd)


def make_path(filename):
  rebuild_path(filename)
  d, f = os.path.split(filename)
  if (not (os.path.exists(d))):
    recursive_mkdir(d)

def default_handler(in_stream):
  content = in_stream.read()
  return content

def gzip_handler(in_stream):
  content = gzip.GzipFile(fileobj=StringIO.StringIO(in_stream.read())).read()
  return content

handlers={"gzip": gzip_handler}

def get_handler(response):
  t = response.getheader("content-encoding")
  try:
    return handlers[t]
  except:
    return default_handler

def parse_http_response( ins ):
  resp =reponse (fakesocket(ins))
  resp.begin()
  return resp
  
def unpack_header(line):
  index = line.find(":")
  if (index != -1):
    return line[:index], line[index+1:]
  return None, None

def build_key(dic, line):
  key, value = unpack_header(line)
  key = key.strip().lower()
  dic[key]=value.strip()


def rebuild_path(path):
  if (path == "/"):
    return
  isFile =  os.path.isfile(path)
  if (isFile):
    tmp_target = os.tmpnam()
    ext = os.path.splitext(path)[-1]
    shutil.move(path, tmp_target)
    recursive_mkdir(path)
    shutil.move(tmp_target, os.path.join (path, "index"+ext  ))
  parent , child = os.path.split(path)
  rebuild_path(parent)

def make_filename(server_ip, request, response):
  try:
    hostname = request.headers["host"]
  except:
    hostname = server_ip
  filename = os.path.join(request.start.prefix, hostname, request.url[1:])
  content_type ="text/plain"
  try:
    content_type = response.getheader("content-type").split(";")[0]
  except:
    pass
  extensions = mimetypes.guess_all_extensions(content_type)
  coherent_extension = False
  for extension in extensions:
    if (filename.endswith(extension)):
      coherent_extension = True
      break;  
  if (not (coherent_extension )):
    ext = mimetypes.guess_extension(content_type)
    if (ext != None):
      filename +="/index" + ext
  return os.path.normpath(filename)

class base_state (object):
  def get_url(self):
    return "undefined"
  def get_request_headers(self):
    return {}
  def get_response_headers(self):
    return {}
  def get_value(self, name):
    return ""

def remove_path(path):
    try:
	os.remove(path)
    except Exception, e:
      pass
    try:
      for root, dirs, files in os.walk(path, topdown=False):
	  for name in files:	      
	      os.remove(os.path.join(root, name))
	  for name in dirs:
	      os.rmdir(os.path.join(root, name))
      os.rmdir(path)
    except Exception, e:
      pass

class response_state (base_state):
  def __init__(self, request):
    self.request = request
    self.content = None
  def parse(self, instream):
    self.content = instream.read()
    self.resp = parse_http_response( StringIO.StringIO(self.content))
    return self
  def print_obj(self):
    resp = self.resp
    if (resp.status == 200):
      filename = make_filename(self.request.start.d["dest-ip"], self.request, resp)
      remove_path(filename)
      handler = get_handler(resp)
      content = handler(resp)
      make_path(filename)
      out = open(filename, "wb")
      try:
	out.write(content)
      finally:
	out.close()
  def not_last(self):
      return self.content == None
  def get_url(self):
    return self.request.get_url()
  def get_request_headers(self):
    return  self.request.headers
  def get_response_headers(self):
    return self.resp.getheaders()
  def get_value(self, name):
    return self.request.start.get_value(name)

class request_state (base_state):
  def __init__(self, start):
    self.counter = 0
    self.start = start
    self.headers={}
    self.result = True
  def parse(self, instream):
    while (True):
      line = instream.readline()
      nline =line.strip()    
      if (len (nline) == 0) :return response_state(self)
      if (self.counter == 0):
	lineparts = nline.split()
	self.method, self.url, self.response = lineparts[0], lineparts[1], lineparts[2]
	if (self.method != "GET"): 
	  self.result =False
	  return self
      else:
	build_key(self.headers, line)
      self.counter +=1
  def not_last(self):
      return self.result
  def get_url(self):
      try:
	return "http://"+self.headers["host"]+self.url
      except:
	return "http://"+self.start.d["dest-ip"]+self.url

  def get_request_headers(self):
    return  self.headers
  def get_response_time(self):
    return self.start.get_response_time()

class start_state (base_state):
  def __init__(self, prefix):
    self.d ={}
    self.prefix=prefix
  def parse(self, instream):
    while (True):
      line = sys.stdin.readline()
      if (line == "\n") :return request_state(self)
      build_key(self.d, line)
  def not_last(self):
      return True
  def get_value(self, name):
    return self.d[name]

url =""
content =""
try:
  prefix= directory
  state = start_state(prefix)
  while (state.not_last()):
    state= state.parse(sys.stdin)
    try:
      url = state.get_url()
    except:
      pass
    try:
      content = state.content
    except:
      pass

  print  state.get_value("connection-time") + "\t" + \
    state.get_value("idle-time-0") + "\t" + \
    state.get_value("request-time")+ "\t"+ \
    state.get_value("response-time")+ "\t"+ \
    state.get_value("idle-time-1") + "\t" + \
    state.get_value("response-size")+ "\t"+ \
    state.get_url()

  state.print_obj()

except httplib.IncompleteRead, e:
  raise Exception ("ERROR httplib.IncompleteRead-  url: http://"+ url)

#except Exception, e:
  #print "ERROR "+ repr(e)
  #print "url: http://"+ url
  #print "content: " + str(len(content))
  #print content
