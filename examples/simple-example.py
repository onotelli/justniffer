import re

# Use the following command to extract relevant network information. 
# It will print the source IP, source port, destination IP, destination port, 
# request headers, and response headers—but only for HTTP requests.
#
# 
#
# sudo justniffer -P simple-example.py  -i any -l "%source.ip:%source.port %dest.ip:%dest.port%newline%request.header%newline%response.header"

HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

def app(log: bytes):
    print('-' * 190)
    is_http = False
    for idx, line in enumerate(log.decode('utf-8', errors='ignore').splitlines()):
        if idx == 0:
            print(line)
        if idx == 1:
            for method in HTTP_METHODS:
                if line.startswith(method):
                    is_http = True
                    break
        if  is_http:
            print(line)
