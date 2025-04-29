from typing import Any, cast
from enum import Enum, auto
from dataclasses import dataclass
from justniffer.model import Conn, ExchangeBase
from justniffer.logging import logger
from justniffer.tsl_info import get_TLSInfo, TLSContent, TLSInfo, ServerHelloMsg, TLSVersion

CONNECTION_TIMEOUT = 5

METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT')
counts = 0

@dataclass
class TLSConnectionInfo:
    server_name_list :list[str] | None
    sid: bytes
    version: TLSVersion | None
    cipher: str | None
    def __repr__(self) -> str:
        return f'{self.server_name_list[0] if self.server_name_list else None} {self.version} {self.cipher}'

@dataclass
class Connection:
    conn : Conn
    tls: TLSConnectionInfo | None = None


connections:dict[Conn, Connection] = {}

class Status(Enum):
    init = auto()
    opening = auto()
    open = auto()
    request = auto()
    response = auto()
    close = auto()
    interrupted = auto()
    timed_out = auto()


@dataclass
class Event:
    status: Status


@dataclass
class TimedEvent(Event):
    ts: float | None = None


class Collector(ExchangeBase):

    def name(self) -> str:
        return self.__class__.__name__

    def value(self, connection:Connection) -> Any: ...

    def update_res(self, res: dict, connection:Connection) -> None:
        res[self.name()] = self.value(connection)


class ResponseTime(Collector):
    _response_time: float | None
    _request_time: float | None

    def __init__(self) -> None:
        super()
        self._response_time = None
        self._request_time = None

    def on_request(self, conn: Conn, content, time: float) -> None:
        self._request_time = time

    def on_response(self, conn: Conn, content, time: float) -> None:
        self._response_time = time

    def value(self, connection: Connection) -> Any:
        if self._response_time is not None and self._request_time is not None:
            return self._response_time - self._request_time
        else:
            return None
MAX_BITS = 2**64
class ConnectionID(Collector):
    def value(self, connection:Connection) -> Any:
        pos_hash = hash(connection.conn) % (MAX_BITS)
        return hex(pos_hash )

class TLSInfoCollector(Collector):
    _request: bytes | None
    _response: bytes | None

    def __init__(self) -> None:
        super()
        self._request = None
        self._response = None

    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        if (self._request is None):
            self._request = content
        else:
            self._request += content

    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        if (self._response is None):
            self._response = content
        else:
            self._response += content

    def value(self, connection:Connection) -> Any:
        
        if connection.tls is None:
            server_name_list,  cipher , version , sid= None, None, None, None
            if self._request is not None:
                tls_info = get_TLSInfo(self._request)
                if tls_info is not None and isinstance(tls_info, TLSInfo):
                    server_name_list = get_sni(tls_info)
                    for msg in tls_info.msgs or []:
                        if sid is None:
                            sid = getattr(msg, 'sid',  None)
            if self._response is not None:
                tls_info = get_TLSInfo(self._response)
                if tls_info is not None and isinstance(tls_info, TLSInfo) :
                    for msg in tls_info.msgs:
                        cipher = getattr(msg, 'cipher',  None)
                        version = getattr(msg, 'version',  None)
                        if sid is None: 
                            sid = getattr(msg, 'sid', None)
                    if version is None:
                        version = tls_info.version
            if (sid is not None):
                if version is None:
                    logger.warning(self._request)
                    logger.warning(self._response)
                if cipher is None:
                    logger.warning(self._request)
                    logger.warning(self._response)
                
                connection.tls = TLSConnectionInfo(server_name_list, sid, version, cipher)
            else:
                if connection.conn[1][1] == 443:
                    logger.warning(self._request)
    
        return connection.tls
        res: list[TLSContent] = []
        if self._request is not None:
            res.append(get_TLSInfo(self._request))
        if self._response is not None:
            res.append(get_TLSInfo(self._response))
        return res



def get_sni(tls: TLSContent | None) -> list[str] | None:
    if hasattr(tls, 'msgs'):
        msgs = getattr(tls, 'msgs', list())
        for msg in msgs:
            name = getattr(msg,  'sni_list', None)
            if name is not None:
                return name
    return None


class DestIP(Collector):
    ip: str
    port: int

    def on_opening(self, conn: Conn, time: float) -> None:
        self._setup_info(conn)

    def _setup_info(self, conn):
        self.ip, self.port = conn[-1]

    def on_open(self, conn: Conn, time: float) -> None:
        self._setup_info(conn)

    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        self._setup_info(conn)

    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        self._setup_info(conn)

    def on_close(self, conn: Conn, time: float) -> None:
        self._setup_info(conn)

    def on_timed_out(self, conn: Conn, time: float) -> None:
        self._setup_info(conn)

    def value(self, connection:Connection) -> Any:
        return self.ip, self.port


class Composite(Collector):
    _elements: tuple[Collector, ...]

    def __init__(self, elements: tuple[Collector, ...]) -> None:
        super()
        self._elements = elements

    def on_opening(self, conn: Conn, time: float) -> None:
        for e in self._elements:
            e.on_opening(conn, time)

    def on_open(self, conn: Conn, time) -> None:
        for e in self._elements:
            e.on_open(conn, time)

    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        for e in self._elements:
            e.on_request(conn, content, time)

    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        for e in self._elements:
            e.on_response(conn, content, time)

    def on_close(self, conn: Conn, time: float) -> None:
        for e in self._elements:
            e.on_close(conn,  time)

    def on_timed_out(self, conn: Conn, time: float) -> None:
        for e in self._elements:
            e.on_timed_out(conn,  time)

    def on_interrupted(self) -> None:
        for e in self._elements:
            e.on_interrupted()

    def value(self, connection:Connection) -> Any:
        return [e.value(connection) for e in self._elements]

def setup_connection(conn: Conn) -> Connection:
    connection = connections.get(conn)
    if connection is None:
        connection = Connection(conn)
        connections[conn] = connection
    logger.debug(f'connections = {len(connections)}')
    return connection

def remove_connection (conn:Conn) -> Connection:
    connection = connections.pop(conn)
    logger.debug(f'connections = {len(connections)}')
    return connection
    

class Exchange(Composite):
    _events: list[Event]
    _conn: Conn | None

    def __init__(self) -> None:
        global counts
        super().__init__((ConnectionID(),DestIP(), ResponseTime(), TLSInfoCollector()))
        self._events = []
        self._events.append(Event(Status.init))
        counts += 1
        self._conn = None
        logger.debug(f'__init__ {counts=} {id(self)=} ')
        self._connection_to_be_removed = False

    def _setup_conn(self, conn: Conn) -> None:
        if self._conn is not None:
            assert self._conn == conn
        else:
            self._conn = conn
            setup_connection(conn)

    def on_opening(self, conn: Conn, time: float) -> None:
        super().on_opening(conn, time)
        self._setup_conn(conn)
        self._events.append(TimedEvent(Status.opening, time))
        logger.debug(f'on_opening {id(self)=}  {conn=} ')

    def on_open(self, conn: Conn, time) -> None:
        super().on_open(conn, time)
        self._setup_conn(conn)
        self._events.append(TimedEvent(Status.open, time))
        logger.debug(f'on_open {id(self)=}  {conn} {type(time)}')

    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        super().on_request(conn, content, time)
        self._setup_conn(conn)
        self._events.append(TimedEvent(Status.request, time))
        logger.debug(f'on_request {id(self)=} {conn=}')
        logger.debug(repr(content))

    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        super().on_response(conn, content, time)
        self._setup_conn(conn)
        self._events.append(TimedEvent(Status.response, time))
        logger.debug(f'on_response {id(self)=}  {conn=} ')
        logger.debug(repr(content))

    def on_close(self, conn: Conn, time: float) -> None:
        super().on_close(conn,  time)
        self._setup_conn(conn)
        self._events.append(TimedEvent(Status.close, time))
        logger.debug(f'on_close {id(self)=}  {conn=} ')
        self._connection_to_be_removed = True

    def on_interrupted(self) -> None:
        super().on_interrupted()
        self._events.append(Event(Status.interrupted))
        logger.debug(f'on_interrupted  {id(self)=} ')
        self._connection_to_be_removed = True

    def on_timed_out(self, conn: Conn, time: float) -> None:
        super().on_timed_out(conn, time)
        self._events.append(TimedEvent(Status.timed_out, time))
        logger.debug(f'on_timed_out  {id(self)=} {conn=} ')
        self._connection_to_be_removed = True

    def result(self) -> str | None:
        if self._conn is None:
            logger.warning(f'{id(self)=} {counts=} {self._conn=} {self._events}')
        else:
            connection = connections[self._conn]
            logger.info(self.value(connection))
            if self._connection_to_be_removed:
                remove_connection(self._conn)
            
            # logger.info(f'{id(self)=} {counts=} {self._conn=} {self._events}')
        return None

    def __del__(self) -> None:
        global counts
        counts -= 1
        logger.debug(f'__del__ {counts=} {id(self)=}  ')


app = Exchange
