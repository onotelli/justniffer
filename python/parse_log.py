#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
#0-1%request.timestamp 2%request.timestamp2 3%request.header.host 4%source.ip:%source.port 
# 5%dest.ip:%dest.port 6%request.method 7%request.url 
#8 %request.size 9 %response.code 10 %response.size 11%connection 
# 12 %close.originator 13 %connection.time 14 %request.time 15 %idle.time.0 
#16 %response.time 17 %idle.time.1 18 %close.time
#19 %response.header.grep(^\s*Content-Type:\s*([^\s]*))
import types
import datetime
import graph

def median(numbers, perc = .5):
  n = len(numbers)
  copy = sorted (numbers)
  if n & 1:
    return copy[n // int(1/perc)]
  else:
    return (copy[n // int(1/perc) - 1] + copy[n // int (1/perc)]) / (1/perc)

class collector(object):

  def parse_fields(self, field):
    pass

  def print_result(self):
    pass

def print_html(*args):
  res = "<tr>"
  for arg in args:
    res+="<td>"+str(arg)+"</td>"
  res += "</tr>"
  print res

def print_2(*args):
  print args
  #try:
    ##print "%.02f"%args[1] ,","
    #print "\""+args[2]+"\"" ,","
  #except:
    #pass
    
print_=print_2

class printer:
  def begin():
    pass
  def title(title_):
    pass
  def row(*fields):
    pass
  def end():
    pass

def simple_print(printer, key, value):
  printer.begin()
  printer.title(key)
  printer.row(value)
  printer.end()

class requests_per_sec(collector):
  def __init__(self):
    self._min = None
    self._max = None
    self._count = 0

  def parse_fields(self, fields):
    t = float (fields[2])
    if (self._min == None):
      self._min = t
    if (self._max == None):
      self._max = t
    self._min = min(self._min, t)
    self._max = max(self._max, t)
    self._count += 1

  def print_result(self, printer):
    simple_print(self.get_title(), int(float(self._count)/(self._max -self._min)))

class elapsed(requests_per_sec):
   def print_result(self):
    print_ (self.__class__.__name__)
    print_ (datetime.timedelta(seconds=self._max -self._min))

class hits(requests_per_sec):
   def print_result(self):
    print_ (self.__class__.__name__)
    print_ (self._count)


class base_collector(collector):
  def __init__(self, columns, groupby = None, max_ = 10):
    if (type(columns) == types.ListType):
      self._columns = columns
    else:
      self._columns = [columns]
    if (groupby == None):
      self._groupby = []
    else:
      if (type(groupby) == types.ListType):
	self._groupby = groupby
      else:
	self._groupby = [groupby]
    self._max = max_
    self._values = dict()

  def parse_fields(self, fields):
    if (self.is_to_include(fields)):
      try:
	key = self.get_key(fields)
	value = self.get_values(fields)
	self.update_values(key, value)
      except ValueError:
	pass

  def get_values(self, fields):
    vals = []
    for col in self._columns:
      vals.append(fields[col])
    return self.get_value(vals)

  def is_to_include(self, fields):
    return True

  def get_key(self, fields):
    if (self._groupby == None):
      d = self._columns
    else:
      d = self._groupby
    res = ""
    first = True
    for col in d:
      if (not first): res += " "
      res +=fields[col]
      first = False
  
    return res

  def get_title(self):
    return self.__class__.__name__

  def print_result(self):
    print_ (self.get_title())
    count = 0
    found_others = False
    for k, v in self.get_items():      
      if (count > self._max) and (self._max != -1):
	found_others = True
	self.update_others(k, v)
      else:
	self.print_item(k, v)
	count +=1
    if (found_others):
      self.print_others() 

  def get_items(self):
    return sorted (self._values.items(), lambda x, y: int (y[1] -x[1]))

  def print_item(self, key, value):
    print_ (value, key)

  def get_value(self, vals):
    res = 0
    for val in vals:
      res += float(val)
    return res


class percentable(base_collector):
  def __init__(self, columns, groupby = None, max_ = 10):
    base_collector.__init__(self, columns, groupby , max_)
    self.others = 0
    self.__values = list()
    self.__labels = list()

  def print_item(self, key, value):
    print_ (value , self.get_percent(value), key)
    self.__values.append(value)
    self.__labels.append(key)

  def update_others(self, key, value):
    self.others += value

  def print_others(self):
    self.print_item("others", self.others)

  def print_result(self):
    base_collector.print_result(self)
    graph.create_graph_file("./ciccio.png", self.get_title(), self.__values, self.__labels)


class count(percentable):
  def __init__(self, groupby , max_ = 10):
    percentable.__init__(self, [], groupby , max_)
    self.tot = 0

  def update_values(self, key, value):
    if not (self._values.has_key(key)):
      self._values[key] = 1
    else:
      self._values[key] += 1
    self.tot+=1  

  def get_value(self, vals):
    return None

  def get_percent(self, value):
    return float(value)/self.tot*100

class sum_(percentable):
  def __init__(self, columns, groupby = None, max_ = 10):
    percentable.__init__(self, columns, groupby , max_)
    self.tot = 0

  def update_values(self, key, value):
    if not (self._values.has_key(key)):
      self._values[key] = value
    else:
      self._values[key] += value
    self.tot += value

  def get_percent(self, value):
    return float(value)/self.tot*100

class calc_base(base_collector):
  def __init__(self, columns, groupby = None, max_ = 10):
    base_collector.__init__(self, columns, groupby , max_)
    self.others = []

  def update_others(self, key, value):
    self.others.append(value)

class median_(calc_base):
  def update_values(self, key, value):
    if not (self._values.has_key(key)):
      self._values[key] = [value]
    else:
      self._values[key].append(value)

  def get_items(self):
    for k, v in self._values.items():
      m = median (v)
      self._values[k] = m
    return sorted (self._values.items(), lambda x, y: int (y[1] -x[1]))

  def print_others(self):
    print_ ("others", median(self.others))

class average(calc_base):

  def update_values(self, key, value):
    if not (self._values.has_key(key)):
      self._values[key] = (value, 1)
    else:
      sum, count = self._values[key]
      self._values[key] = (sum +value, count +1)

  def print_result(self):
    print_ (self.__class__.__name__)
    count = 0
    for k, v in sorted (self._values.items(), lambda x, y: int ((y[1][0]/ y[1][1])-(x[1][0]/ x[1][1]))):
      count +=1
      print_ (v[0]/ v[1], k)
      if count > self._max: break

class max_(calc_base):

  def update_values(self, key, value):
    if not (self._values.has_key(key)):
      self._values[key] = value
    else:
      val = self._values[key]
      self._values[key] = max (val, value)

 
def get_all_lines(filename):
  f = open (filename)
  return f

    #t = {
    #"connection": 13,
    #"request": 14,
    #"idle0": 15,
    #"response": 16,
    #"idle1": 17,
    #"close": 18,
    #"host": 3,
    #"dest": 5,
    #"source": 4,
    #"method": 6,
    #"req_size": 8,
    #"resp_size": 10,
    #"resp_code": 9,
    #"url": 7,
    #"close_orig":12,
    #"conn_type":11
    #"content_type":19

    #}


#l = [average(18), 
      #median_(18, 3),
#average(16,3),
    #sum_([10, 8], 3),
     #count(3, 3),
     #requests_per_sec(), elapsed(), hits()]



l = [	
      average([18], [11,12]),
      median_([18], [11,12]),
      max_([13]),
      max_([14]),
      max_([16]),
      max_([17]),
      max_([18])
    ]
#print_ median ([1,2,3,4,5,6,7,8])
counter=0
if __name__ =="__main__":
  for line in get_all_lines(sys.argv[1]):
    fields = line.split()
    if (len (fields)!= 20): 
      #print_ line, len (fields), counter
      pass
    else:
      for c in l:
	c.parse_fields(fields)
    counter+=1
  for c in l: 
    c.print_result(console_printer)

#c.print_result()
#print_ (func(get_all_lines(sys.argv[1]),col))