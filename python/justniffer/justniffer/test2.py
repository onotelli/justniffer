from datetime import datetime
import re
import sys
from enum import Enum
from time import time
from loguru import logger
import os

from justniffer.model import Conn

logger.remove()


logger.add(sys.stderr)
counter = 0


class Status(str, Enum):
    syn = 'syn'
    established = 'established'
    closed = 'closed'
    refused = 'refused'
    truncated = 'truncated'

class Connection:
    _status: Status
    _request_time : float | None
    _response_time : float | None
    def __init__(self) -> None:
        global counter
        counter += 1
        self._id = time()
        logger.debug(f'__init__ {counter} {self._id=}')
        self._conn: Conn| None = None
        self._time = None
        self._request_time = None
        self._response_time = None
        self._request = b''
        self._response = b''
        self._status = Status.syn

    def on_open(self, conn: Conn, time) -> None:
        logger.debug(f'on_open {self._id=} {conn} {type(time)}')
        self._status = Status.established
        self._init_conn(conn, time)

    def _init_conn(self, conn: Conn, time):
        if self._conn is None:
            self._conn = conn
            self._time = time

    def on_request(self, conn: Conn, bytes, time:float) -> None:
        logger.debug(f'on_request {self._id=} {conn=}')
        self._init_conn(conn, time)
        self._request_time = time
        self._request += bytes
        

    def on_response(self, conn:Conn, bytes:bytes, time:float) -> None:
        logger.debug(f'on_response {self._id=} {conn=} ')
        self._init_conn(conn, time)
        self._response_time = time
        self._response += bytes


    def on_opening(self, conn: Conn, time: float) -> None:
        t = datetime.fromtimestamp(time)
        logger.debug(f'on_opening {self._id=} {conn=} ')


    def on_close(self, conn: Conn, time: float) -> None:        
        self._status = Status.refused if self._status == Status.syn else Status.closed
        self._init_conn(conn, time)
        logger.debug(f'on_close {self._id=} {conn=} ')


    def on_interrupted(self) -> None:
        self._status = Status.truncated
        logger.debug(f'on_interrupted {self._id=} {self._conn=} ')

    def result(self) -> str | None:
        if self._conn and self._request is not None and self._time is not None:
            req = self._get_first_part(self._request)
            res = self._get_first_part(self._response)
            logger.info( f'{os.getuid()} {self._status} {datetime.fromtimestamp(self._time)} | {self._conn} | {req} | {res}')
        return None

    def _get_first_part(self, content: bytes| None) -> str:
        req :bytes = b''
        if content is not  None:
            pos = content.find(b'\n')
            if pos != -1:
                req  = content[:min(pos, 40)]
        return re.sub(r'[\x00-\x1F\x7F]', '', req.decode(errors="ignore"))
    
    def __del__ (self) -> None:
        global counter
        counter -= 1
        logger.debug(f'__del__ {counter} {self._conn} {self._id=} {self._status=}')

app = Connection

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

