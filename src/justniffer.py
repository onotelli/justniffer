import sys
sys.argv=["justiffer"]

import _justniffer
from collections import OrderedDict

class dict_object(dict):
    def __getattr__(self, name):
        return self[name]
    
    def __dir__(self):
        return self.keys()

BaseHandler = _justniffer.BaseHandler
class BaseImpl(BaseHandler):

    def __calc_time(self, time1, time0):
            values = self.values
            if values.has_key(time1) and values.has_key(time0):
                return values[time1]-values[time0]
    
    def _guess_protocol(self, request, response):
        try:
            part = response[:4]
            part.decode("ascii")
            prot =  part.strip().upper()
        except:
            prot = "".join(["\\"+hex(ord(p)) for p in part])
        return prot
    
    def __update_string_value(self, name, value):
        values = self.req_resp
        
        if not values.has_key(name):
            values[name]=value
        else:
            values[name]+=value
        
    def __init__(self):
        BaseHandler.__init__(self)
        self.values = dict_object()
        self.req_resp = dict_object()
        self.__onRequest_start_time=None
        self.__onRespone_start_time=None

    def onClose(self, stream, time):
        self.values["close_end_time"] = time
        
    def onOpening(self, stream, time):
        values = self.values
        values["source_ip"] = stream.src_ip
        values["source_port"] = stream.src_port
        values["dest_ip"] = stream.dst_ip
        values["dest_port"] = stream.dst_port
        self.values["opening_end_time"] = time
        
    def onOpen(self, stream, time):
        values = self.values
        values["source_ip"] = stream.src_ip
        values["source_port"] = stream.src_port
        values["dest_ip"] = stream.dst_ip
        values["dest_port"] = stream.dst_port
        self.values["open_end_time"] = time
        
    def onExit(self, stream):
        pass
        
    def onRequest(self, stream, time):
        values = self.values
        values["source_ip"] = stream.src_ip
        values["source_port"] = stream.src_port
        values["dest_ip"] = stream.dst_ip
        values["dest_port"] = stream.dst_port
        if (not values.has_key("request_start_time")):
            values["request_start_time"] = time
        values["request_end_time"] = time
        self.__update_string_value("request", stream.client_data)
        
    def onResponse(self, stream, time):
        values = self.values
        if (not values.has_key("response_start_time")):
            values["response_start_time"] = time
        values["response_end_time"] = time
        self.__update_string_value("response", stream.server_data)

    def __get_val(self, name, time):        
        if self.values.has_key(name):
            val = self.values[name]
        else:
            val = None
        return val
        
    def __get_reqrep_size(name):        
        def __call__(self, name_, time):
            if self.req_resp.has_key(name):
                val = len(self.req_resp[name])
            else:
                val = 0
            return val
        return __call__
        
    def __get_protocol(self, name, time):
        values = self.req_resp
        if values.has_key("response") and values.has_key("request"):
            protocol = self._guess_protocol(values.request,values.response)
        else:
            protocol=None
        return protocol
    
    def __ct(time1, time0):
        def __call__(self, name, time):
            return self.__calc_time(time1, time0)
        return __call__
    
    def __calc_idle_time_1(self, name, time):
        values = self.values
        idle_time_1=None
        if values.has_key("response_end_time"):
            if values.has_key("close_end_time"):
                idle_time_1 = self.__calc_time ("close_end_time" , "response_end_time")
            elif values.has_key("response_end_time"):
                idle_time_1 =  time - values.response_end_time
        return idle_time_1
    
    def __type_in_stream(self, name, time):
        values = self.values
        connection_time = values.connection_time
        close_time = values.close_time
        first = True if connection_time else False 
        last = True if close_time else False 
        continue_  = not (first and last)
        unique  = first and last
        if unique:
            type_="unique"
            
        elif continue_:
            type_="continue"
        elif first:
            type_="first"
        elif last:
            type_="last"
        else:
            type_="unknown"
        return type_

    @classmethod
    def on_exit(cls):
        pass
        
    od = OrderedDict
    attributes = od((
        ("response_size",__get_reqrep_size("response")),
        ("request_size",__get_reqrep_size("request")),
        ("protocol",__get_protocol),
        ("response_time",__ct("response_end_time" ,"request_end_time")),
        ("connection_time",__ct ("open_end_time" , "opening_end_time")),
        ("close_time",__ct ("close_end_time" , "response_end_time")),
        ("req_resp_time",__ct ("response_end_time" , "request_start_time")),
        ("idle_time_0",__ct ("response_start_time" , "request_end_time")),
        ("idle_time_1",__calc_idle_time_1),
        ("type_in_stream",__type_in_stream))
    )

    def append(self, outstream, time):
        values = self.values
        for attribute_name, func in self.attributes.items():
            attribute = func(self, attribute_name, time)
            values[attribute_name]= attribute
        self._on_complete(values, time)

    def _on_complete(self, values, time):
        pass

class Test(BaseImpl):
    def _on_complete(self, values, time):
        print values
    
    
def on_exit():
    print "on_exit"
