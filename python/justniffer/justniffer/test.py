from abc import abstractmethod, ABC
from typing import Any, Iterable,  cast
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass
from justniffer.model import Conn
from justniffer.logging import logger
from justniffer.tls_info import TLSVersion, parse_tls_content as get_TLSInfo, TlsRecordInfo as TLSInfo
from justniffer.http_info import parse_http_content

CONNECTION_TIMEOUT = 5

METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT')
counts = 0

SEP = ' '


def _to_str(value: Any | None) -> str:
    if isinstance(value, str):
        return value
    elif value is None:
        return '-'
    else:
        return str(value)


def float_to_str(v: float) -> str:
    return f'{v:.4f}'


@dataclass
class TLSConnectionInfo:
    server_name_list: list[str] | None
    sid: bytes
    version: TLSVersion | None
    cipher: str | None
    common_name: str | None
    organization_name: str | None
    expires: datetime | None

    def __repr__(self) -> str:
        return f'{_to_str(self.server_name_list[0] if self.server_name_list else None)} {_to_str(self.version)} {_to_str(self.cipher)} {_to_str(self.common_name)} {_to_str(self.organization_name)} {_to_str(self.expires.strftime("%Y-%m-%d %H:%M:%S") if self.expires else None)}'


@dataclass
class Connection:
    conn: Conn
    tls: TLSConnectionInfo | None = None


connections: dict[Conn, Connection] = {}


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
    ts: float


@dataclass
class ContentEvent(TimedEvent):
    ts: float
    content: bytes


@dataclass
class RequestEvent(ContentEvent):
    def __init__(self, content: bytes, time: float):
        super().__init__(content=content, ts=time, status=Status.request)


@dataclass
class ResponseEvent(ContentEvent):
    def __init__(self, content: bytes, time: float):
        super().__init__(content=content, ts=time, status=Status.response)


def _get_content(events: Iterable[Event], class_: type) -> bytes:
    return b''.join(map(lambda event: cast(ContentEvent, event).content, filter(lambda event: isinstance(event, class_), events)))


def response(events: Iterable[Event]) -> bytes:
    response = _get_content(events, ResponseEvent)
    return response


def request(events: Iterable[Event]) -> bytes:
    request = _get_content(events, RequestEvent)
    return request


class Extractor(ABC):
    @abstractmethod
    def value(self, connection: Connection, events: list[Event]) -> str | None: ...


class RequestSize(Extractor):
    def value(self, connection: Connection, events: list[Event]) -> str | None:
        return str(len(request(events)))


class ResponseSize(Extractor):
    def value(self, connection: Connection, events: list[Event]) -> str | None:
        return str(len(response(events)))


class ResponseTime(Extractor):

    def value(self, connection: Connection, events: list[Event]) -> str | None:
        last_request = None
        first_response = None
        for event in events:
            if last_request is None and isinstance(event, TimedEvent) and event.status is Status.request:
                last_request = event
            if first_response is None and isinstance(event, TimedEvent) and event.status is Status.response:
                first_response = event
            if last_request and first_response:
                break
        if last_request is not None and first_response is not None:
            return float_to_str(first_response.ts - last_request.ts)
        else:
            return None


MAX_BITS = 2**64


class ConnectionID(Extractor):
    def value(self, connection: Connection, events: list[Event]) -> Any:
        pos_hash = hash(connection.conn) % (MAX_BITS)
        return hex(pos_hash)


def to_date_string(dt: float):
    # with milliseconds
    return datetime.fromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S.%f')


class RequestTimestamp(Extractor):
    def value(self, connection: Connection, events: list[Event]) -> str | None:
        req: TimedEvent | None = cast(TimedEvent, next(filter(lambda event: isinstance(event, TimedEvent) and event.status is Status.request, events), None))
        if req is not None:
            return to_date_string(req.ts)
        else:
            req = cast(TimedEvent, next(filter(lambda event: isinstance(event, TimedEvent), events), None))
            if req is not None:
                return to_date_string(req.ts)
        return None


class ContentExtractor(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def value(self, connection: Connection, events: list[Event], request: bytes, response: bytes) -> str | None: ...


class TLSInfoExtractor(ContentExtractor):
    name = 'TLS'  # type: ignore

    def value(self, connection: Connection, events: list[Event], request: bytes, response: bytes) -> str | None:
        if connection.tls is None:
            server_name_list,  cipher, version, sid = None, None, None, None
            common_name, organization_name, expires = None, None, None
            if request is not None:
                tls_info = get_TLSInfo(request)
                if tls_info is not None and isinstance(tls_info, TLSInfo):
                    server_name_list = get_sni(tls_info)
                    for msg in tls_info.messages or []:
                        if sid is None:
                            sid = getattr(msg, 'sid',  None)
            if response is not None:
                tls_info = get_TLSInfo(response)
                if tls_info is not None and isinstance(tls_info, TLSInfo):
                    for msg in tls_info.messages:
                        if cipher is None:
                            cipher = getattr(msg, 'cipher',  None)
                        if version is None:
                            version = getattr(msg, 'version',  None)
                        if sid is None:
                            sid = getattr(msg, 'sid', None)
                        if common_name is None:
                            certificate = getattr(msg, 'certificate', None)
                            if certificate is not None:
                                common_name = certificate.common_name
                                organization_name = certificate.organization_name
                                expires = certificate.expires
                    if version is None:
                        version = tls_info.version
            if (sid is not None and response is not None):
                if version is None:
                    logger.warning(request)
                    logger.warning(response)
                if cipher is None:
                    logger.warning(request)
                    logger.warning(response)
                connection.tls = TLSConnectionInfo(server_name_list, sid, version, cipher, common_name, organization_name, expires)
            else:
                if connection.conn[1][1] == 443:
                    logger.warning(request)

        return repr(connection.tls) if connection.tls else None


def get_sni(tls: TLSInfo | None) -> list[str] | None:
    if hasattr(tls, 'messages'):
        msgs = getattr(tls, 'messages', list())
        for msg in msgs:
            name = getattr(msg,  'sni_hostnames', None)
            if name is not None:
                return name
    return None


class HttpInfoExtractor(ContentExtractor):
    name = 'HTTP'  # type: ignore

    def value(self, connection: Connection, events: list[Event], request: bytes, response: bytes) -> str | None:

        res = parse_http_content(request, response)
        request_obj, response_obj = res
        method = request_obj.method if request_obj else None
        url = request_obj.url if request_obj else None
        host_list = request_obj.headers.get('Host') if request_obj else None
        if host_list is None:
            host_list = [_to_str(None)]
        host = host_list[0]
        code = response_obj.code if response_obj else None
        message = response_obj.message if response_obj else None
        version = response_obj.version if response_obj else None
        if request_obj is None and response_obj is None:
            return None
        else:
            return f'{_to_str(version)} {_to_str(method)} {_to_str(url)} {_to_str(host)} {_to_str(code)}'


class DestIPPort(Extractor):

    def value(self, connection: Connection, events: list[Event]) -> str:
        ip, port = connection.conn[1]
        return f'{ip}:{port}'


def setup_connection(conn: Conn) -> Connection:
    connection = connections.get(conn)
    if connection is None:
        connection = Connection(conn)
        connections[conn] = connection
    logger.debug(f'connections = {len(connections)}')
    return connection


def remove_connection(conn: Conn) -> Connection:
    connection = connections.pop(conn)
    logger.debug(f'connections = {len(connections)}')
    return connection


class ProtocolSelector(ContentExtractor):
    _subexector: tuple[ContentExtractor, ...] = (TLSInfoExtractor(), HttpInfoExtractor())
    name = ''  # type: ignore

    def value(self, connection: Connection, events: list[Event], request: bytes, response: bytes) -> str | None:
        for e in self._subexector:
            res = e.value(connection, events, request, response)
            if res is not None:
                return e.name + SEP + res
        return None


class Exchange:
    _events: list[Event]
    _conn: Conn | None
    _extractors: tuple[Extractor | ContentExtractor, ...]

    @property
    def _sep(self) -> str:
        return SEP

    def __init__(self) -> None:
        global counts
        self._extractors = (RequestTimestamp(), ConnectionID(), DestIPPort(), ResponseTime(), RequestSize(), ResponseSize(), ProtocolSelector())
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
        self._setup_conn(conn)
        self._events.append(TimedEvent(Status.opening, time))
        logger.debug(f'on_opening {id(self)=}  {conn=} ')

    def on_open(self, conn: Conn, time) -> None:
        self._setup_conn(conn)
        self._events.append(TimedEvent(Status.open, time))
        logger.debug(f'on_open {id(self)=}  {conn} {type(time)}')

    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        self._setup_conn(conn)
        self._events.append(RequestEvent(content=content, time=time))
        logger.debug(f'on_request {id(self)=} {conn=}')
        logger.debug(repr(content))

    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        self._setup_conn(conn)
        self._events.append(ResponseEvent(content=content, time=time))
        logger.debug(f'on_response {id(self)=}  {conn=} ')
        logger.debug(repr(content))

    def on_close(self, conn: Conn, time: float) -> None:
        self._setup_conn(conn)
        self._events.append(TimedEvent(Status.close, time))
        logger.debug(f'on_close {id(self)=}  {conn=} ')
        self._connection_to_be_removed = True

    def on_interrupted(self) -> None:
        self._events.append(Event(Status.interrupted))
        logger.debug(f'on_interrupted  {id(self)=} ')
        self._connection_to_be_removed = True

    def on_timed_out(self, conn: Conn, time: float) -> None:
        self._events.append(TimedEvent(Status.timed_out, time))
        logger.debug(f'on_timed_out  {id(self)=} {conn=} ')
        self._connection_to_be_removed = True

    def result(self) -> str | None:
        res = None
        if self._conn is None:
            logger.warning(f'{id(self)=} {counts=} {self._conn=} {self._events}')
        else:
            connection = connections[self._conn]
            res = self.value(connection)
            if self._connection_to_be_removed:
                remove_connection(self._conn)

            # logger.info(f'{id(self)=} {counts=} {self._conn=} {self._events}')
        return str(res)

    def value(self, connection: Connection) -> str:
        final_value = ''
        request_ = None
        response_ = None

        def get_request() -> bytes:
            nonlocal request_
            if request_ is None:
                request_ = request(self._events)
            return request_

        def get_response() -> bytes:
            nonlocal response_
            if response_ is None:
                response_ = response(self._events)
            return response_

        for idx, e in enumerate(self._extractors):
            if idx != 0:
                final_value += self._sep
            if isinstance(e, ContentExtractor):
                value = _to_str(e.value(connection, self._events, get_request(), get_response()))
            else:
                value = _to_str(e.value(connection, self._events))
            final_value += value

        return final_value

    def __del__(self) -> None:
        global counts
        counts -= 1
        logger.debug(f'__del__ {counts=} {id(self)=}  ')


app = Exchange
