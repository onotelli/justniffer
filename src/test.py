from _justniffer import BaseImpl

class PythonDerived(BaseImpl):
    def _on_complete(self, values, time):
        print values
    


from webob import Response, Request
from io import BytesIO
from datetime import datetime
import sys
sys.argv=["justiffer"]
from IPython import embed
from mimetypes import guess_extension as _guess_extension
from md5 import md5
from plecnoutils import write_file_content
from os.path import exists, join
from os import makedirs
from gzip import GzipFile
base_dir="/tmp/test_ericsson"
http_methods=("GET", "POST", "OPTIONS", "HEAD", "PUT", "DELETE")

__types={"image/bmp":".bmp", 
        "application/unknown":".data", 
        "multipart/byteranges" :".data"}

def guess_extension(type):
    ext = _guess_extension(type)
    if ext is None:
        ext = __types[type]
    return ext

def default_encoder(body):
    return body.read()

def gzip_encoder(body):
    gzipped_body = GzipFile(fileobj=body)
    unzipped_body = gzipped_body.read()
    return unzipped_body
    
class PythonDerived2(BaseHandler):
    __encoders={"gzip":gzip_encoder, None:default_encoder}
    
    def __init__(self):
        BaseHandler.__init__(self)
        self.request =""
        self.response=""
    
    @property
    def response_time(self):
        t2 = self.time2 or self.time1
        t1 = self.time1 or self.time2
        response_time = t2 -t1
        return response_time
    def onRequest(self, tcp_stream, time):
        self.time1 = time
        self.tcp_stream = tcp_stream
        request_data  = tcp_stream.client_data
        self.request += request_data 

    def onClose(self, tcp_stream, time):
        self.tcp_stream = tcp_stream
        self.time2 = time
    
    def onResponse(self, tcp_stream, time):
        self.time2 = time
        self.tcp_stream = tcp_stream
        self.response += tcp_stream.server_data
        
    def append(self, s, i):
        res = self.result()
        if res:
            msg = "\t".join([str(e) for e in res])
            s.write(msg)
            s.write("\n")
            
    def result(self):
        response_time = self.response_time
        method = self.request[:4].strip()
        if method in http_methods:
            stream = BytesIO(self.request)
            req = Request.from_file(stream)
            params={}
            try:
                params = req.params.mixed()
            except:
                pass
            vars =[req.method, req.path, params, req.referer ]
            if len(self.response):
                stream = BytesIO(self.response)
                resp = Response.from_file(stream)
                if resp.content_length and response_time > 20:
                    self.save_file(req, resp)
                return "{0:.2f}".format(response_time),  "\t".join([str(e) for e in vars])
    
    def formatted_response_time(self, response_time):
        int_part = int (response_time)
        dec_part = response_time-int_part
        return ("%04d"%int_part)+"_"+ ("%.2f"%dec_part)[2:]
        
    
    def save_file(self, req, resp):
        path = req.path
        file_name = "_".join([self.formatted_response_time(self.response_time)]+path.split("/")).strip("_")
        params={}
        try:
            params = req.params.mixed()
        except:
            pass
        if len(params):
            hashed = md5(str(params.items()))
            params_hash = hashed.hexdigest()
            file_name=file_name+"_"+params_hash
        try:
            extension = guess_extension(resp.content_type or "text/plain")
        except:
            embed()
    
        if file_name.endswith(extension):
            full_file_name=file_name
        else:
            full_file_name=file_name+extension
        
        body = BytesIO(resp.body)
        encoder = self.get_encoder(resp.content_encoding)
        try:
            decoded = encoder(body)
        except IOError:
            t, e, tb = sys.exc_info()
            extension = ".txt"
            decoded = str(e)
            full_file_name=file_name+"_ERROR"+extension
            
        if not exists(base_dir):
            makedirs(base_dir)
        file_path= join (base_dir, full_file_name)
        write_file_content(file_path, decoded)
        print "saved_content: ",file_path
        
    def get_encoder(self, encoder_str):
        encoder = self.__encoders [encoder_str]
        return encoder
        
#handler = PythonDerived()

class Test(BaseHandler):
    def append(self,outstream, time):
        print "ok"
        
def on_exit():
    print "on_exit"
