#!/usr/bin/python
# -*- coding: utf-8 -*-
#	Copyright (c) 2009 Plecno s.r.l. All Rights Reserved 
#	info@plecno.com
#	via Giovio 8, 20144 Milano, Italy
#	Released under the terms of the GPLv3 or later
#	Author: Oreste Notelli <oreste.notelli@plecno.com>	
import os
import calendar
import time
import mimetypes
import shutil
import urlparse
import cgi
import string
import hashlib

# back_end
class back_end:
  def save_response(self, request, response):
    pass

  def get_hosts(self):
    pass

  def get_requests(self, host):
    pass

  def get_response(self, request):
    pass

last_mod_formats = ["%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S +0000"]
"""Mon, 20 Apr 2009 10:22:50 GMT"""
"""Thu, 02 Apr 2009 23:56:11 +0000"""
extensions= {\
"text/plain":".txt",
"text/javascript": ".js",
"image/jpeg": ".jpg",
"application/x-www-form-urlencoded": ".txt"
}

admittable = string.ascii_letters + string.digits +"_.-=[](),:;{}"

# file_system_back_end
class file_system_back_end(back_end):
  def __init__(self, base_dir):
    self.base_dir = base_dir

  def save_response(self, request, response):
    filename = self.get_filename(request, response)
    filepath = os.path.abspath(os.path.realpath(os.path.join(self.base_dir, filename)))
    abs_base = os.path.abspath(self.base_dir)
    if (not (filepath.startswith(abs_base))):
      raise Exception(filepath + " is not subdir of "+ abs_base)
    last_modified = response.get_header("Last-Modified")
    if os.path.isfile(filepath):
      if (last_modified != None):
	if not (self.is_file_to_refresh(filepath, last_modified)):
	  return 
    self.make_path(filepath)
    content = response.get_decoded_body()
    if (len (content)> 0):
      out = open(filepath, "wb")
      try:
	out.write(content)
      finally:
	out.close()
	if (last_modified != None):
	  mtstmp = self.timestamp_from_last_modified(last_modified)
	  os.utime(filepath, (mtstmp, mtstmp))

  def get_visited_hosts(self):
    pass

  def get_visited_urls(self, host=None):
    pass


  def get_response(self, request):
    pass

  def timestamp_from_last_modified(self, last_modified):
    for last_mod_format in last_mod_formats:
      try:
	return calendar.timegm(time.strptime( last_modified, last_mod_format))
      except ValueError:
	pass
    return time.time()

  def is_file_to_refresh(self, filepath, last_modified):
    ft = os.path.getmtime(filepath)
    lt = self.timestamp_from_last_modified(last_modified)
    size = os.path.getsize(filepath)
    return  (ft < lt) or (size == 0)

  def get_filename(self, request, response):
    hostname = request.get_header("host")
    if (hostname == None):
      hostname = request.get_ip_address()
    encoded_url = self.encode_url (request.get_url())
    filename = os.path.join(hostname, encoded_url)
    filename += self.get_extension(filename, response)
    return os.path.normpath(filename)
  
  def encode_path(self, url_path):
    return url_path

  def encode_url(self, url):
    p = urlparse.urlparse(url)
    url_path = self.encode_path(p[2].lstrip("/"))  
    query = p[4]
    encoded_query, to_hash= self.encode_query(query)
    
    if len(encoded_query) > 0:
      r = url_path + "?"+ encoded_query
    else:
      r = url_path

    if (len (r) > 200):
      r = r[:190] + "_"+ str(self.hash_function(url))
    elif (to_hash):
	r+="_"+ str(self.hash_function(url))
    return r

  def hash_function(self, value):
    sha = hashlib.sha1(value)
    return sha.hexdigest()

  def encode_param(self, param):
    to_hash = False
    r =""
    for c in param:
      if c  in admittable:
	r+=c
      else:
	r+="_"
	to_hash = True
    return r, to_hash

  def encode_query(self, query):
    d = parsed_query = cgi.parse_qs(query)
    first = True
    r_tohash = False
    s =""
    for key, value in d.items():
      for elem in value:
	if not (first):
	  s += "&"
	enc_param, to_hash  = self.encode_param(key)
	r_tohash |= to_hash
	enc_val , to_hash = self.encode_param(elem)
	r_tohash |= to_hash
	s += enc_param + "=" + enc_val
	first = False
    return s, r_tohash
  
  def get_extension(self, filename, response):
    content_type ="text/plain"
    try:
      content_type = response.get_header("content-type").split(";")[0]
    except:
      pass
    extensions = self.guess_all_extensions(content_type)
    coherent_extension = False
    for extension in extensions:
      if (filename.endswith(extension)):
	coherent_extension = True
	break;  
    if (not (coherent_extension )):
      ext = self.guess_extension(content_type)
      if (ext != None):
	return self.get_missing_extension(ext )
    return ""

  def get_missing_extension(self, ext):
    return "index"+ext

  def make_path(self, filepath):
    if (os.path.isfile(filepath)):
      return
    if (os.path.isdir(filepath)):
      shutil.rmtree(filepath)
      return
    self.rebuild_path(filepath)
    d, f = os.path.split(filepath)
    if (not (os.path.exists(d))):
      self.recursive_mkdir(d)

  def rebuild_path(self, path):
    """ rebuild the path looking if part of it is an existing file
    """
    if (path == "/"):
      return
    isFile =  os.path.isfile(path)
    if (isFile):
      tmp_target = os.tmpnam()
      ext = os.path.splitext(path)[-1]
      shutil.move(path, tmp_target)
      self.recursive_mkdir(path)
      shutil.move(tmp_target, os.path.join (path, "index"+ext  ))
    parent , child = os.path.split(path)
    self.rebuild_path(parent)

  def recursive_mkdir(self, path):
    os.makedirs(path)

  def guess_extension(self, content_type):
    try:
      return extensions[content_type]
    except:
      return mimetypes.guess_extension(content_type)

  def guess_all_extensions(self, content_type):
    l = mimetypes.guess_all_extensions(content_type)
    try:
      l.append(extensions[content_type])
    except:
      pass
    return l

flat_files_back_end_admitted =  string.ascii_letters + string.digits
# flat_files_back_end
class flat_files_back_end(file_system_back_end):

  def encode_url(self, url):
    max =  200
    r = ""
    counter = 0;
    for c in url:
      if c in flat_files_back_end_admitted:
	r += c
      else:
	r += "_"
      counter += 1
      if counter > max:
	r += self.hash_function(url)
	break
    return r

