from datetime import datetime
import sys
import re

env_path = '/opt/midesa/projects/justniffer/tmp/env/test/lib/python3.10/site-packages'
sys.path.insert(0, env_path)
from loguru import logger
logger.remove(0)
logger.add(sys.stderr, format="{time:YYYY-MM-DD at HH:mm:ss!UTC} | {level} | {message}", level="INFO")
counter = 0

class Pippo2:
    def __init__(self) -> None:
        global counter
        counter += 1
        logger.debug(f'__init__ {counter}')
        self._conn = None
        self._time = None
        self._request_time = None
        self._response_time = None
        self._request = b''
        self._response = b''

    def on_open(self, conn, time) -> None:
        logger.debug(f'on_open {conn}')
        self._conn = conn
        self._time = time

    def on_request(self,  bytes, time) -> None:
        logger.debug(f'on_request')
        self._request_time = time
        self._request = bytes

    def on_response(self,  bytes, time) -> None:
        logger.debug(f'on_response')
        self._response_time = time
        self._response = bytes


    def on_interrupted(self) -> None:
        logger.debug('on_interrupted')

    def result(self) -> str | None:
        req :bytes = b''
        if self._conn and self._response_time :
            pos = self._request.find(b'\n')
            if pos != -1:
                req  = self._request[:min(pos, 256)]
            clean_res = re.sub(r'[\x00-\x1F\x7F]', '', req.decode(errors="ignore"))
            print( f'{datetime.fromtimestamp(self._time) if self._time else "N/A"} | {self._conn} | {clean_res}')
        return None
    
    def __del__ (self) -> None:
        global counter
        counter -= 1
        logger.debug(f'__del__ {counter}')



class Pippo:
    def __init__(self) -> None:
        print ('__init__', self)

    def result(self) -> str:
        return 'ok'
    def on_open(self, conn, time) -> None:
        print('on_open', conn, time)

    def on_opening(self, conn, time) -> None:
        t = datetime.fromtimestamp(time)
        print ('on_opening',   time, conn)

    def on_request(self,  content, time) -> None:
        t = datetime.fromtimestamp(time)
        print ('on_request',   time, content[:10])

    def on_close(self, time) -> None:
        print ('on_close',   time)

    def on_response(self,  content, t) -> None:
        print ('on_response',    t, content[:10])

    def on_interrupted(self) -> None:
        print ('on_interrupted')

    def __del__(self) -> None:
        print ('__del__')

def u (*args) -> None:
    print ('fico')
