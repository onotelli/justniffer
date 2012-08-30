import justniffer
    
class PythonDerived(justniffer.BaseHandler):
    def __init__(self):
        justniffer.BaseHandler.__init__(self)
        self.time1 = 0
        self.time2 = 0
        self.request =""
        self.response=""
        #s.write()
    
    def onOpening(self, tcp_stream, time):
        self.tcp_stream = tcp_stream
        
    def onOpen(self, tcp_stream, time):
        self.tcp_stream = tcp_stream
        
    def onRequest(self, tcp_stream, time):
        self.time1 = time
        self.tcp_stream = tcp_stream
        request_data  = tcp_stream.client_data()
        self.request += request_data 
    
    def onResponse(self, tcp_stream, time):
        self.time2 = time
        self.tcp_stream = tcp_stream
        self.response += tcp_stream.server_data()
        
    def onClose(self, tcp_stream, time):
        self.tcp_stream = tcp_stream
        
    def append(self, s, i):
        t2 = self.time2 or self.time1
        t1 = self.time1 or self.time2
        tcp_stream = self.tcp_stream 
        s.write("{time:.2f}\t{src_ip}:{src_port}\t{dst_ip}:{dst_port}\t{len}".format(time=t2-t1, 
                                                                        src_ip=tcp_stream.src_ip(),
                                                                        src_port=tcp_stream.src_port(),
                                                                        dst_ip=tcp_stream.dst_ip(),
                                                                        dst_port=tcp_stream.dst_port(), len=self.request.splitlines()[0] ))


from webob import Response, Request
from io import BytesIO
from datetime import datetime
import sys

class PythonDerived2(justniffer.BaseHandler):
    def __init__(self):
        justniffer.BaseHandler.__init__(self)
        self.request =""
        self.response=""
        
    def onRequest(self, tcp_stream, time):
        self.time1 = time
        self.tcp_stream = tcp_stream
        request_data  = tcp_stream.client_data()
        self.request += request_data 

    def onClose(self, tcp_stream, time):
        self.tcp_stream = tcp_stream
        self.time2 = time
    
    def onResponse(self, tcp_stream, time):
        self.time2 = time
        self.tcp_stream = tcp_stream
        self.response += tcp_stream.server_data()
        
    def append(self, s, i):
        res = self.result()
        if res:
            msg = "\t".join([str(e) for e in res])
            s.write(msg)
        else:
            s.write("NOT_APPLICABLE")
        
    def result(self):
        try:
            t2 = self.time2 or self.time1
            t1 = self.time1 or self.time2
            response_time = t2 -t1
            stream = BytesIO(self.request)
            req = Request.from_file(stream)
            #params = "&".join ( ["{k}={v}".format(k=k, v=v) for k , v in req.params.mixed().items()])
            vars =[req.method, req.path]
            if len(self.response) and req.method == "GET":
                stream = BytesIO(self.response)
                resp = Response.from_file(stream)
                return  response_time,  "\t".join([str(e) for e in vars])
        except:
            pass


#handler = PythonDerived()
