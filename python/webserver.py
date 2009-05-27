#!/usr/bin/python
# -*- coding: utf-8 -*-
#	Copyright (c) 2009 Plecno s.r.l. All Rights Reserved 
#	info@plecno.com
#	via Giovio 8, 20144 Milano, Italy
#	Released under the terms of the GPLv3 or later
#	Author: Oreste Notelli <oreste.notelli@plecno.com>	

import SimpleHTTPServer
import BaseHTTPServer
import urlparse
import urllib
import os
import posixpath
import string
from StringIO import StringIO
import cgi
import mimetypes
# minimal web server.  serves files relative to the
# current directory.

def is_of_main_content_type(path, content_type):
  try:
    return mimetypes.guess_type(path)[0].split("/")[0].startswith(content_type)    
  except:
    return False

def is_image(path):
  return is_of_main_content_type(path, "image")

def is_text(path):
  return is_of_main_content_type(path, "text")

docuemnt_root = "/tmp/pippo/" 

class dir_link:
  def __init__(self, path, name):
    self.path = path
    self.name = name
  def get_html(self):
    displayname = self.name + "/"
    linkname = self.name + "/"
    linkname = urllib.quote(linkname)
    return '<li><a href="%s">%s</a>\n' % (linkname, cgi.escape(displayname))

class link_link:
  def __init__(self, path, name):
    self.path = path
    self.name = name
  def get_html(self):
    displayname = self.name + "@"
    linkname = self.name + "/"
    linkname = urllib.quote(linkname)
    return '<li><a href="%s">%s</a>\n' % (linkname, cgi.escape(displayname))

class host_link:
  def __init__(self, path, name):
    self.path = path
    self.name = name
  def get_html(self):
    linkname="http://"+self.name
    displayname = linkname
    return '<li><a href="%s">%s</a>\n' % (linkname, cgi.escape(displayname))

class None_link:
  def __init__(self, path, name):
    self.path = path
    self.name = name
  def get_html(self):
    displayname = self.name
    linkname = self.name 
    linkname = urllib.quote(linkname)
    return '<li><a href="%s">%s</a>\n' % (linkname, cgi.escape(displayname))

class img_link:
  def __init__(self, path, name):
    self.path = path
    self.name = name
  def get_html(self):
    linkname = self.name
    linkname = urllib.quote(linkname)
    return '<li><img src="%s"></img>\n' % (linkname)

class text_link:
  def __init__(self, path, name):
    self.path = path
    self.name = name
  def get_html(self):
    linkname = self.name
    linkname = urllib.quote(linkname)
    return '<li><iframe src="%s"></iframe>\n' % (linkname)


class MyHTTPRequestHandler (SimpleHTTPServer.SimpleHTTPRequestHandler):
  def __init__(self, *args, **kargs):
    return SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kargs)

  def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
	parsed = urlparse.urlparse(path)
	host = parsed[1]
	if (host.startswith("localhost")): host =""
        path = parsed[2]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = string.rstrip(self.get_root()+host, "/")
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
	print "path=%s"%(path)
        return path

  def list_directory(self, path):
	"""Helper to produce a directory listing (absent index.html).

	Return value is either a file object, or None (indicating an
	error).  In either case, the headers are sent, making the
	interface the same as for send_head().

	"""
	try:
	    list = os.listdir(path)
	except os.error:
	    self.send_error(404, "No permission to list directory")
	    return None
	list.sort(key=lambda a: a.lower())
	f = StringIO()
	displaypath = cgi.escape(urllib.unquote(self.path))
	f.write("<title>Directory listing for %s</title>\n" % displaypath)
	f.write("<h2>Directory listing for %s</h2>\n" % displaypath)
	f.write("<hr>\n<ul>\n")
	for name in list:
	    fullname = os.path.join(path, name)
	    displayname = linkname = name
	    l = None_link(path, name)
	    # Append / for directories or @ for symbolic links
	    if os.path.isdir(fullname):
		l = dir_link(path, name)
	    if os.path.islink(fullname):
		l = link_link(path, name)
	    if (os.path.isfile(fullname)):
	      if (is_image(fullname)):
		l = img_link(path, name)
	      elif (is_text(fullname)):
		l = text_link(path, name)
		# Note: a link to a directory displays with @ and links with /
	    if (path.rstrip("/") == docuemnt_root.rstrip("/")):
		l = host_link(path, name)

	    f.write(l.get_html())
	f.write("</ul>\n<hr>\n")
	length = f.tell()
	f.seek(0)
	self.send_response(200)
	self.send_header("Content-type", "text/html")
	self.send_header("Content-Length", str(length))
	self.end_headers()
	return f

  def get_root(self):
      #return self.root
	return docuemnt_root


def MyFactory(root):
  def _Factory(*args, **kargs):
    h = MyHTTPRequestHandler(*args, **kargs)
    setattr(h, "root", root)
    return h
  return _Factory

PORT = 8000

Handler = MyHTTPRequestHandler

httpd = BaseHTTPServer.HTTPServer(("", PORT), MyFactory(docuemnt_root))

print "serving at port", PORT
httpd.serve_forever()

