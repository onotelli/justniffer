# -*- coding: utf-8 -*-
#import hashlib

class content_type(object):
  pass

def _hash(value):
  return hash(str(value))

class cache (object):
  def __init__(self, f):
    self.f = f
    self.values =dict()
    

  def __call__(self, *args, **kargs):
    h = _hash((args, kargs))
    if not self.values.has_key(h):
      r = self.f(*args, **kargs)
      self.values[h] = r
    else:
      r = self.values[h]
    return r
