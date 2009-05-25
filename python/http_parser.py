#!/usr/bin/python 
# -*- coding: utf-8 -*-
import sys
import StringIO
import string
import httplib
import mimetools
import mimetypes
import signal
import os
import shutil
import commands
import time
import calendar
import gzip
import urlparse
import cgi
from optparse import OptionParser


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
  def readline(self):
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

extensions= {\
"text/plain":".txt",
"text/javascript": ".js",
"application/x-www-form-urlencoded": ".txt"
}

def make_path(filepath):
  if (os.path.isfile(filepath)):
    return
  if (os.path.isdir(filepath)):
    shutil.rmtree(filepath)
    return
  rebuild_path(filepath)
  d, f = os.path.split(filepath)
  if (not (os.path.exists(d))):
    recursive_mkdir(d)

def recursive_mkdir(path):
  cmd = "mkdir -p \""+path+"\""
  s, o=  commands.getstatusoutput(cmd)
  if (s != 0):
    raise Exception(" mkdir  error: "+ cmd + " - "+ o)

def guess_extension(content_type):
  try:
    return extensions[content_type]
  except:
    return mimetypes.guess_extension(content_type)

def guess_all_extensions(content_type):
  l = mimetypes.guess_all_extensions(content_type)
  try:
    l.append(extensions[content_type])
  except:
    pass
  return l

admittable = string.ascii_letters + string.digits +"_.-=[](),:;{}"

def encode_param(param):
  to_hash = False
  r =""
  for c in param:
    if c  in admittable:
      r+=c
    else:
      r+="_"
      to_hash = True
  return r, to_hash


def encode_query(query):
  d = parsed_query = cgi.parse_qs(query)
  first = True
  r_tohash = False
  s =""
  for key, value in d.items():
    for elem in value:
      if not (first):
	s += "&"
      enc_param, to_hash  = encode_param(key)
      r_tohash |= to_hash
      enc_val , to_hash = encode_param(elem)
      r_tohash |= to_hash
      s += enc_param + "=" + enc_val
      first = False
  return s, r_tohash

def encode_url(url):
  p = urlparse.urlparse(url)
  url_path = p[2].lstrip("/")
  query = p[4]
  encoded_query, to_hash= encode_query(query)
  
  if len(encoded_query) > 0:
    r = url_path + "?"+ encoded_query
  else:
    r = url_path

  if (len (r) > 200):
    r = r[:190] + "_"+ str(hash(url))
  elif (to_hash):
      r+="_"+ str(hash(url))
  return r

def make_filename(default_hostname, request, response):
  hostname = request.get_header("host")
  if (hostname == None):
    hostname = default_hostname
  encoded_url = encode_url (request.get_url())
  filename = os.path.join(hostname, encoded_url)
  content_type ="text/plain"
  try:
    content_type = response.get_header("content-type").split(";")[0]
  except:
    pass
  extensions = guess_all_extensions(content_type)
  coherent_extension = False
  for extension in extensions:
    if (filename.endswith(extension)):
      coherent_extension = True
      break;  
  if (not (coherent_extension )):
    ext = guess_extension(content_type)
    if (ext != None):
      filename +="/index" + ext
  return os.path.normpath(filename)

def gzip_handler(body):
  content = gzip.GzipFile(fileobj=StringIO.StringIO(body)).read()
  return content

HTTPMessage_handlers={"gzip": gzip_handler}


def rebuild_path(path):
  """ rebuild the path looking if part of it is an existing file
  """
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

last_mod_formats = ["%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S +0000"]
"""Mon, 20 Apr 2009 10:22:50 GMT"""
"""Thu, 02 Apr 2009 23:56:11 +0000"""

def timestamp_from_last_modified(last_modified):
  for last_mod_format in last_mod_formats:
    try:
      return calendar.timegm(time.strptime( last_modified, last_mod_format))
    except ValueError:
      pass
  return time.time()

def is_file_to_refresh(filepath, last_modified):
  ft = os.path.getmtime(filepath)
  lt = timestamp_from_last_modified(last_modified)
  return  ft < lt

def save_content_to_file(base_dir, request, response):
  filename = make_filename("default", request, response)
  filepath = os.path.abspath(os.path.realpath(os.path.join(base_dir, filename)))
  abs_base = os.path.abspath(base_dir)
  if (not (filepath.startswith(abs_base))):
    raise Exception(filepath + " is not subdir of "+ abs_base)
  last_modified = response.get_header("Last-Modified")
  if os.path.isfile(filepath):
    if (last_modified != None):
      if not (is_file_to_refresh(filepath, last_modified)):
	return 
  make_path(filepath)
  content = response.get_decoded_body()
  out = open(filepath, "wb")
  try:
    out.write(content)
  finally:
    out.close()
    if (last_modified != None):
      mtstmp = timestamp_from_last_modified(last_modified)
      os.utime(filepath, (mtstmp, mtstmp))
  

def print_info(in_, base_dir):
  requests , response_line= get_requests(in_)
  if (response_line != None):
    responses = get_responses(in_, response_line)
  index =0
  for request in requests:
    method, url, rest = request.first_line.split(None, 2)
    host = request.get_header("host")
    response = responses[index] 
    response_code = response.first_line.split()[1]
    if (response_code == "200"):
      print ("---------------------------------------------------------")
      print "saving file.. ",make_filename("default", request, response)
      print "from ",method, host, url 
      print "of type '" +str( response.get_header("content-type"))+"'"
      save_content_to_file(base_dir, request, response)
    index +=1

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

try:
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
