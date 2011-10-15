#!/usr/bin/python 
# -*- coding: utf-8 -*-
#	Copyright (c) 2009 Plecno s.r.l. All Rights Reserved 
#	info@plecno.com
#	via Giovio 8, 20144 Milano, Italy
#	Released under the terms of the GPLv3 or later
#	Author: Oreste Notelli <oreste.notelli@plecno.com>	

import sys
import StringIO
import httplib
import mimetools
import os
import gzip
from optparse import OptionParser
import common


def list_to_str(list_):
  first = True
  result = ""
  for element in list_:
    if not first:
      result +=", "
    result += elem_to_str(element)
    first = False
  return result

def elem_to_str(elem):
  return str(elem).replace("\r", "\\r").replace("\n", "\\n")

def dict_to_str(dict_):
  first = True
  result = ""
  for key, value in dict_.items():
    if not first:
      result +=", "
    result += str(key)+ "="+ elem_to_str(value)
    first = False
  return result

def test(function):
  def call( *args, **kargs):
    print function.__name__, "(" ,list_to_str( args), dict_to_str( kargs), ")"
    result = function(*args, **kargs)
    print function.__name__+ " returned: '" + elem_to_str(result)+"'"
    return result
  return call
  #return function

class proxy(object):
  def __init__(self, o):
    self.o = o
    self.first=False
    self.first_line =None
    self.c=""
  def reset(self):
    self.c=""
  def __getattr__(self, name):
    try:
      result = self.__dict__[name]
      return result
    except:
      return getattr(self.o, name)
  def readline(self, max=None):
    if self.first:
      self.first = False
      return self.first_line+"\n"
    else:
      line= self.o.readline()
      self.c+=line
      return line
  def close(self, *arg):
    #return self.o.close(*arg)
    pass
  def read(self, *arg):
    res = self.o.read(*arg)
    self.c+=res
    return res

def gzip_handler(body):
  content = gzip.GzipFile(fileobj=StringIO.StringIO(body)).read()
  return content

HTTPMessage_handlers={"gzip": gzip_handler}

class HTTPMessage:
  def __init__(self, first_line, mimeMessage, body):
    self.first_line = first_line
    self.word1 , self.word2= first_line.split()[:2]
    self.mimeMessage = mimeMessage
    self.body = body
  def get_url(self):
    return self.word2
  def get_code(self):
    return self.word2
  def get_method(self):
    return self.word1
  def get_body(self ):
    return self.body
  def get_header(self, name):
    return self.mimeMessage.getheader(name)
  def get_headers(self, name):
    return self.mimeMessage.getheaders(name)
  def all_headers(self):
    return self.mimeMessage.headers
  def get_decoded_body(self):
    body = self.get_body()
    encoding = self.get_header("content-encoding")
    if (encoding != None):
      decoder = HTTPMessage_handlers[encoding]
      return decoder(body)
    else:
      return body


http_methods = ["GET",
"HEAD",
"POST",
"PUT",
"DELETE",
"TRACE",
"CONNECT"]

class fake_socket:
  def __init__(self, fp):
    self.fp = fp
  def makefile(self, *args):
    return self.fp

def  fake_fp(first_line, fp):
  fp.first= True
  fp.first_line =first_line
  return fp
  
def is_newline(c):
  return c in "\n"

def readline(in_):
  c = in_.read(1)
  line = str()
  while (len (c)>0):
    if (is_newline (c)):
      line+=c
      break
    line+=c
    c = in_.read(1)
  return line

def is_request(first_line):
  try:
    first_word = first_line.split()[0]
    return first_word in http_methods
  except:
    return False

def is_response(first_line):
  try:
    first_word = first_line.split()[0]
    return first_word.startswith("HTTP/")
  except:
    return False

def get_body(in_, content_length):
  return in_.read(content_length)

def get_message(in_):
  header = find_until_newline(in_)
  message = mimetools.Message(StringIO.StringIO(header))
  content_length = message.getheader("content-length")
  body = ""
  if (content_length != None):
    content_length = int (content_length)
    body= get_body(in_, content_length)
  return httplib.HTTPMessage(StringIO.StringIO(header+body)), body

def get_requests(in_):
  requests=[]
  first_line = None
  while(True):
    first_line = readline(in_)
    if is_request(first_line):
      request = get_message(in_)
      requests.append(HTTPMessage(first_line, request[0], request[1]))
    else:
      break
  return requests, first_line

def get_responses(in_, response_line):
  responses=[]
  first_line = response_line
  while(len (first_line) > 0):
    fake_fp(first_line, in_)
    response = httplib.HTTPResponse(fake_socket(in_))
    response.begin()
    try:
      body = response.read()
    except httplib.IncompleteRead, e:
      body =""
    responses.append(HTTPMessage(first_line, response.msg, body))
    first_line = readline(in_)
    if not is_response(first_line): break
  return responses

def find_until_newline(in_):
  return find_until(in_, lambda line: len (line.strip())==0)

def find_until(in_, is_to_break):
  c =""
  line = readline(in_)
  while (not is_to_break(line)):
    c+=line
    line = readline(in_)
  return c


def save_content_to_file(base_dir, request, response):
  #be = common.file_system_back_end(base_dir)
  be = common.flat_files_back_end(base_dir)
  be.save_response(request, response)

def print_info(in_, base_dir):
  requests , response_line= get_requests(in_)
  if (response_line != None):
    responses = get_responses(in_, response_line)
  index =0
  for request in requests:
    try:
      method, url, rest = request.first_line.split(None, 2)
      host = request.get_header("host")
      response = responses[index] 
      response_code = response.first_line.split()[1]
      if (response_code == "200"):
	print ("---------------------------------------------------------")
	#print "saving file.. ",make_filename("default", request, response)
	print "from ",method, host, url 
	print "of type '" +str( response.get_header("content-type"))+"'"
	save_content_to_file(base_dir, request, response)
      index +=1
    except IndexError: 
	  print ("---------------------------------------------------------")
	  print "from ",method, host, url 
	  print "empty response (truncated connection)"
    


try:
    in_ =proxy(sys.stdin)

    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory",
                      help="Directory where to save files")

    (options, args) = parser.parse_args()

    if (options.directory == None):
      parser.print_help()
      sys.exit(-1)

    if (os.geteuid() == 0):
      print "ERROR: "+sys.argv[0]+ " cannot run as root!!!"
      sys.exit(-1)
    print_info(in_, options.directory)
except Exception,e :
    import traceback
    print "*********************ERROR BEGIN*********************"
    t,v,tb = sys.exc_info()
    traceback.print_exception(t,v,tb)
    print "*****************************************************"
    print in_.c
    print "*****************************************************"
    print str(e)
    print "*********************ERROR END***********************"
