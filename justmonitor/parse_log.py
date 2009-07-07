#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
#0-1%request.timestamp 2%request.timestamp2 3%request.header.host 4%source.ip:%source.port 
# 5%dest.ip:%dest.port 6%request.method 7%request.url 
#8 %request.size 9 %response.code 10 %response.size 11%connection 
# 12 %close.originator 13 %connection.time 14 %request.time 15 %idle.time.0 
#16 %response.time 17 %idle.time.1 18 %close.time
#19 %response.header.grep(^\s*Content-Type:\s*([^\s^;]*))
import types
import datetime
#import graph

def percentile (numbers, perc):
  copy = sorted (numbers)
  return copy[int(0.5+(perc*len(numbers)/100))]

def median(numbers):
  return percentile(numbers, 50)
  
def create_str(lst, sep):
  first = True
  res = ""
  for e in lst:
    if (not first) and (len(str(e)) >0):
      res+= sep
    res  += str(e)
    first = False
  return res

class collector(object):
  fieldmap =     {
    "request_timestamp": 2,
    "connection_time": 13,
    "request_time": 14,
    "idle0_time": 15,
    "response_time": 16,
    "idle1_time": 17,
    "close_time": 18,
    "host": 3,
    "dest": 5,
    "source": 4,
    "method": 6,
    "req_size": 8,
    "resp_size": 10,
    "resp_code": 9,
    "url": 7,
    "close_orig":12,
    "connection_type":11,
    "content_type":19 }


  @staticmethod
  def get_column_numbers(lst):
    newlst = []
    for e in lst:
      newlst.append(collector.fieldmap[e])
    return newlst

  def get_title(self):
    return self.__class__.__name__

  def parse_fields(self, field):
    pass

  def print_result(self, printer):
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
  def begin(self):
    pass
  def title(self, title_):
    pass
  def row(self, *fields):
    pass
  def end(self):
    pass

class console_printer(printer):
  def __init__(self):
    self.rows =[]
  def title(self, title_):
    self.title_ = title_
  def row(self, key, *fields):

    if len (key) == 0:
      self.rows.append(( "value", fields))
    else:
      self.rows.append(( key, fields))
  def end(self):
    print self.title_
    for row in self.rows:
      print row
    print

import json

class myEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.timedelta):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

def json_dumps(el):
  return json.dumps(el, cls=myEncoder)

class javascript_printer(printer):
  def __init__(self, out):
    self.rows =[]
    self.__out = out
  def title(self, title_):
    self.title_ = title_
  def row(self, key, *fields):

    if len (key) == 0:
      self.rows.append(( "value", fields))
    else:
      self.rows.append(( key, fields))
  def end(self):
    t = self.title_.replace(" ", "_")
    out = self.__out
    if len(self.rows) == 1 :
      out.write(json_dumps (t))
      out.write(": ")
      out.write(json_dumps (self.rows[0][1][-1]))
      out.write("\n")
    else:
      out.write(json_dumps(t))
      out.write(": ")
      out.write(json_dumps (self.rows))
      out.write("\n")
  
def simple_print(printer, key, value):
  printer.begin()
  printer.title(key)
  printer.row(key, value)
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
    simple_print(printer, self.get_title(), float(self._count)/(self._max -self._min))

class elapsed(requests_per_sec):
   def print_result(self, printer):
    simple_print(printer, self.get_title() ,datetime.timedelta(seconds=self._max -self._min))

class start_time(requests_per_sec):
   def print_result(self, printer):
    simple_print(printer, self.get_title() , datetime.datetime.fromtimestamp(self._min).ctime())

class end_time(requests_per_sec):
   def print_result(self, printer):
    simple_print(printer, self.get_title() , datetime.datetime.fromtimestamp(self._max).ctime())


class hits(requests_per_sec, printer):
   def print_result(self, printer):
    simple_print(printer, self.get_title() ,self._count)


class base_collector(collector):
  def __init__(self, columns, groupby = None, max_ = 10):
    self.__orig_columns = columns
    if (groupby == None):
      self._orig_groupby  = []
    else:
      self._orig_groupby = groupby
    if (type(columns) == types.ListType):
      self._columns = collector.get_column_numbers(columns)
    else:
      self._columns = collector.get_column_numbers([columns])
    if (groupby == None):
      self._groupby = []
    else:
      if (type(groupby) == types.ListType):
	self._groupby = collector.get_column_numbers(groupby)
      else:
	self._groupby = collector.get_column_numbers([groupby])
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
      if (not first):
	res += " "
      res +=fields[col]
      first = False
  
    return res

  def get_title(self):
    res = [self.__class__.__name__]
    res.extend (self.__orig_columns)
    res.extend (self._orig_groupby)
    return create_str( res , " ")

  def print_result(self, printer):
    printer.begin()
    printer.title(self.get_title())
    count = 0
    found_others = False
    for k, v in self.get_items():      
      if (count > self._max) and (self._max != -1):
	found_others = True
	self.update_others(k, v)
      else:
	self.print_item(printer, k, v)
	count +=1
    if (found_others):
      self.print_others(printer) 
    printer.end()

  def get_items(self):
    return sorted (self._values.items(), lambda x, y: int (y[1] -x[1]))

  def print_item(self, printer, key, value):
    printer.row( key, value)

  def get_value(self, vals):
    res = 0
    for val in vals:
      res += float(val)
    return res


class percentable(base_collector):
  def __init__(self, columns, groupby = None, max_ = 10):
    base_collector.__init__(self, columns, groupby , max_ =max_)
    self.others = 0

  def print_item(self,printer,  key, value):
    printer.row(key , self.get_percent(value), value)
    #printer.row(key , value)

  def update_others(self, key, value):
    self.others += value

  def print_others(self, printer):
    self.print_item(printer, "others", self.others)

  def print_result(self, printer):
    base_collector.print_result(self, printer)


class count(percentable):
  def __init__(self, groupby , max_ = 10):
    percentable.__init__(self, [], groupby=groupby , max_=max_)
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

class count_source_ip(count):
  def __init__(self, groupby = None, max_ = 10):
    count.__init__(self, ["source"], max_=max_)

  def get_key(self, fields):
    return fields[self._groupby[0]].split(":")[0]

class count_domain(count):
  def __init__(self, groupby = None, max_ = 10):
    count.__init__(self, ["host"], max_=max_)

  def get_key(self, fields):
    field = fields[self._groupby[0]]
    try:
      dn_parts = field.split(".")
      return dn_parts[-2] + "."+dn_parts[-1]
    except:
      return field

class count_content_type(count):
  def __init__(self, groupby = None, max_ = 10):
    count.__init__(self, ["content_type"], max_=max_)

  def get_key(self, fields):
    return fields[self._groupby[0]].split("/")[0]

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
    base_collector.__init__(self, columns, groupby = groupby, max_ = max_)
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

  def print_others(self, printer):
    printer.row ("others", median(self.others))

class average(calc_base):

  def update_values(self, key, value):
    if not (self._values.has_key(key)):
      self._values[key] = (value, 1)
    else:
      sum, count = self._values[key]
      self._values[key] = (sum +value, count +1)

  def print_result(self, p):
    p.begin()
    p.title(self.get_title())
    count = 0
    for k, v in sorted (self._values.items(), lambda x, y: int ((y[1][0]/ y[1][1])-(x[1][0]/ x[1][1]))):
      count +=1
      p.row ( k, v[0]/ v[1])
      if count > self._max: break
    p.end()

class keep_alive_count(count):
  def __init__(self, max_=10):
    count.__init__(self, ["connection_type"], max_ = max_)

  def get_key(self, fields):
    key = count.get_key(self, fields)
    if (key in ["start", "last", "continue"]):
      return "keepalive"
    if (key in ["unique"]):
      return "no-keepalive"
    else:
      return "unkown"
    
class count_close_originator(count):
  def __init__(self, max_=10):
    count.__init__(self, ["close_orig"], max_ = max_)

  def is_to_include(self, fields):
    return fields[self._groupby[0]] != "-"


class percentiles(median_):
  base = median_
  def __init__(self, columns, includeMax =True, groupby = None, max_ = 10):
    self.__includeMax = includeMax
    median_.__init__(self, columns, groupby , max_)

  def get_percentiles(self, v):
    r = range(1,10)
    d = 10
    p = list ()
    for a in r:
      p.append(percentile (v, a*d))
    if (self.__includeMax):
      p.append(sorted(v)[-1])
    return p
    #return percentile (v, 10), (v, 20), percentile (v, 57), percentile (v, 90)
  def get_title(self):
    title = percentiles.base.get_title(self)
    if (self.__includeMax):
      title += "_max"
    return title

  def get_items(self):
    for k, v in self._values.items():
      self._values[k] = self.get_percentiles(v)
    values =  sorted (self._values.items(), lambda x, y: int (y[1][0] -x[1][0]))
    #print values, self._values
    return values

  def print_others(self, printer):
    v =self.others
    printer.row ("others", self.get_percentiles(v))

class max_(calc_base):
  def __init__(self, columns, groupby = None, max = 10):
    calc_base.__init__(self, columns, groupby = groupby, max_ = max)

  def update_values(self, key, value):
    if not (self._values.has_key(key)):
      self._values[key] = value
    else:
      val = self._values[key]
      self._values[key] = max (val, value)

  def print_others(self, printer):
    pass
    #printer.row ("others", max (self.others))

class max_source_ip(max_):
  def __init__(self, columns, groupby = None, max=10):
    g = ["source"]
    if (groupby  != None):
      if type(groupby) == types.ListType:
	g.extend(groupby)
      else:
	g.append(groupby)
    max_.__init__(self,columns, groupby = g, max = max)    

  def get_key(self, fields):
    key = fields[self._groupby[0]]
    key = max_.get_key(self, fields)
    try:
      key = key.split(":")[0]
    except:
      pass
    
    if (len(self._groupby) > 1):
      for e in self._groupby[1:]:
	key += " " + str(fields[e])
    return key


class percentiles_close_time_server(percentiles):
  def __init__(self ,includeMax = True):
    percentiles.__init__(self, ["close_time"],groupby=["close_orig"], includeMax = includeMax)
  def is_to_include(self, fields):
    return fields[self._groupby[0]] == "server"

class percentiles_close_time_client(percentiles):
  def __init__(self, includeMax = True):
    percentiles.__init__(self, ["close_time"],groupby=["close_orig"], includeMax = includeMax)
  def is_to_include(self, fields):
    return fields[self._groupby[0]] == "client"

class sum_source_ip(sum_):
  def __init__(self, columns, max_ = 10):
    sum_.__init__(self, columns, ["source"] , max_= max_)

  def get_key(self, fields):
    key = sum_.get_key(self, fields)
    try:
      key = key.split(":")[0]
    except:
      pass
    return key


class sum_domain(sum_):
  def __init__(self, columns, max_ = 10):
    sum_.__init__(self, columns, ["host"] , max_= max_)

  def get_key(self, fields):
    field = fields[self._groupby[0]]
    try:
      dn_parts = field.split(".")
      return dn_parts[-2] + "."+dn_parts[-1]
    except:
      return field

class sum_content_type(sum_):
  def __init__(self, columns, max_ = 10):
    sum_.__init__(self, columns, ["content_type"] , max_= max_)

  def get_key(self, fields):
    return fields[self._groupby[0]].split("/")[0]

 
def get_all_lines(filename):
  f = open (filename)
  return f
  def is_to_include(self, fields):
    return fields[self._groupby[0]] != "-"


  #fieldmap =     {
    #"request_timestamp": 2,
    #"connection_time": 13,
    #"request_time": 14,
    #"idle0_time": 15,
    #"response_time": 16,
    #"idle1_time": 17,
    #"close_time": 18,
    #"host": 3,
    #"dest": 5,
    #"source": 4,
    #"method": 6,
    #"req_size": 8,
    #"resp_size": 10,
    #"resp_code": 9,
    #"url": 7,
    #"close_orig":12,
    #"connection_type":11
    #"content_type":19 }



#print_ median ([1,2,3,4,5,6,7,8])
filename = "/home/oreste/Projects/justniffer/justniffer-0.5.6/test/internal2"
#filename = "/tmp/external"
#filename = "/home/oreste/Projects/justniffer/justniffer-0.5.6/test/test2.log"
try:
  filename = sys.argv[1]
except:
  pass

def create_javascript(out):
  l = [	
	count(["host"]),
	count(["dest"]),
	count(["method"]),
	hits(),
	percentiles(["connection_time"]),
	percentiles(["request_time"]),
	percentiles(["idle0_time"]),
	percentiles(["response_time"]),
	percentiles(["idle1_time"]),
	percentiles(["close_time"]),
	percentiles(["connection_time"], includeMax=False),
	percentiles(["request_time"], includeMax=False),
	percentiles(["idle0_time"], includeMax=False),
	percentiles(["response_time"], includeMax=False),
	percentiles(["idle1_time"], includeMax=False),
	percentiles(["close_time"], includeMax=False),
	elapsed(),
	start_time(),
	end_time(),
	requests_per_sec(),
	keep_alive_count(),
	count(["resp_code"]),
	count(["content_type"]),
	count(["host","url"], max_ = 20), 
	count_source_ip(),
	count_domain(),
	count_content_type(),
	count_close_originator(),
	percentiles_close_time_server(),
	percentiles_close_time_client(),
	percentiles_close_time_server(includeMax= False),
	percentiles_close_time_client(includeMax=False),
	sum_(["req_size","resp_size"]),
	sum_source_ip(["req_size","resp_size"]),
	sum_domain(["req_size","resp_size"]),
	sum_content_type(["req_size","resp_size"]),
	sum_(["req_size","resp_size"], ["dest"]),
	sum_(["req_size","resp_size"], ["host"]),
	sum_(["req_size","resp_size"], ["method"]),
	sum_(["req_size","resp_size"], ["content_type"]),
	max_(["req_size","resp_size"], ["host"]) ,
	max_(["req_size","resp_size"], ["host", "url"]),
	max_(["response_time"], ["host"]),
	max_(["response_time"], ["host", "url"]),
	max_(["close_time"], ["host"]),
	max_(["close_time"], ["host", "url"]),
	max_(["request_time"], ["host"]),
	max_(["request_time"], ["host", "url"]),
	max_(["connection_time"],["host"]),
	max_source_ip(["connection_time"]),
	max_source_ip(["idle0_time"]),
	max_source_ip(["idle1_time"], ["url"])
      ]
  print "create_javascript"
  counter=0
  for line in get_all_lines(filename):
    #print line
    fields = line.split()
    if (len (fields)!= 20): 
      print line, len (fields), counter
      pass
    else:
      for c in l:
	c.parse_fields(fields)
    counter+=1
  out.write ("(result = {\n")
  first = True
  for c in l: 
    if not first:
      out.write (",\n")
    c.print_result(javascript_printer(out))
    first = False
  out.write ("})")
  out.flush()
  return out

if __name__ =="__main__":
  create_javascript(sys.stdout)
  #create_javascript(sys.stdout)

#c.print_result()
#print_ (func(get_all_lines(sys.argv[1]),col))