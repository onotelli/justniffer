#!/usr/bin/python
# -*- coding: utf-8 -*-
#	Copyright (c) 2009 Plecno s.r.l. All Rights Reserved 
#	info@plecno.com
#	via Giovio 8, 20144 Milano, Italy
#	Released under the terms of the GPLv3 or later
#	Author: Oreste Notelli <oreste.notelli@plecno.com>	

import baseweb
import parse_log
from config import *

def test(*args, **kargs):
  return args, kargs

import sys
import cairo
import pycha.pie

import pycha.bar

import StringIO

def __pieChart(output, lines):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 300)
    dataSet = [(line[0], [[0, line[1]]]) for line in lines]
    options = {
        'axis': {
            'x': {
                'ticks': [dict(v=i, label=d[0]) for i, d in enumerate(lines)],
            'hide': True,
            }
        },
        'background': {
            'hide': True
        },
        'padding': {
            'left': 150,
            'right': 4,
            'top': 0,
            'bottom': 0,
        },
      'colorScheme': color_scheme,
      'legend': {'opacity':.5,'position': {'left':4}},
    }
    chart = pycha.pie.PieChart(surface, options)
    chart.addDataset(dataSet)
    chart.render()
    surface.write_to_png(output)

def __barChart(output, lines):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 300)

    dataSet = (
        ('Lines', [(i, l[1]) for i, l in enumerate(lines)]),
        
        )

    options = {
        'axis': {
            'x': {
                'ticks': [dict(v=i, label=l[0]) for i, l in enumerate(lines)],
                'rotate': 25,
            },
        },
	'colorScheme': color_scheme,
        'legend': {
            'hide': True
        },
        'padding': {
            'right': 50,
            'bottom': 75,
        }
    }
    chart = pycha.bar.VerticalBarChart(surface, options)
    chart.addDataset(dataSet)
    chart.render()
    surface.write_to_png(output)

def desc(v1,v2):
  return asc (v2, v1)


def asc(v1,v2):
  a = float(v1[1])
  b = float(v2[1])
  return cmp(a, b)

  
  return int(float(v1[1]) - float(v2[1]))

def lex_asc(v1, v2):
  a = v1[0].lower()
  b = v2[0].lower()
  return cmp(a, b)

def __convert_values(args, order_func = desc):
  l = list()
  if (order_func == None):
      copy = args
  else:
    copy = sorted (args, order_func )
  for k, v in sorted (args, order_func ):
    l.append((k, float(v)))
  return l



class base_conten_type (baseweb.content_type):
  def __init__(self, fileObj, _type):
    self._file = fileObj
    self._type = _type

  def get_content(self):
    self._file.seek(0)
    return self._file

  def get_content_type(self):
    return self._type

  def get_content_length(self):
    return self._file.len


class image_png (base_conten_type):
  def __init__(self, fileObj):
    base_conten_type.__init__(self ,fileObj, "image/png")


class text_javascript (base_conten_type):
  def __init__(self, fileObj):
    base_conten_type.__init__(self ,fileObj, "text/javascript")

def make_pie(**kargs):
  res = StringIO.StringIO()
  __pieChart(res , __convert_values(kargs.items()))
  return image_png(res)

def make_bar(*keys, **kargs):
  res = StringIO.StringIO()
  __barChart(res , __order(dict(__convert_values(kargs.items(), None)), keys))
  return image_png(res)

def __order(values, keys):
  l = list()
  for key in keys:
    l.append((key, values[key]))
  return l
  #return values.items()
    

def parse_logs():
  res = StringIO.StringIO()
  parse_log.create_javascript(res)
  return text_javascript(res)
  
  

  