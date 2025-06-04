from abc import abstractmethod, ABC
from typing import Any, Iterable,  cast, Literal
from datetime import datetime
from dataclasses import dataclass

import string
from justniffer.class_utils import ClassDef, TypedPluginManager
from justniffer.model import (CloseEvent, Conn, Connection, ContentEvent, Event, ExchangeBase,
                              ExtractorResponse, ProtocolInfo, RequestEvent, ResponseEvent,
                              Status, TLSConnectionInfo, TimedEvent)
from justniffer.logging import logger
from justniffer.tls_info import parse_tls_content as get_TLSInfo, TlsRecordInfo as TLSInfo
from justniffer.http_info import parse_http_content, DEFAULT_CHARSET
from justniffer.ssh_info import ssh_info, extract_kexinit_info
from justniffer.formatters import get_formatter, to_str, JSONFormatter
from justniffer.extractors import BaseExtractor, ContentExtractor, TypedContentExtractor
from justniffer.config import load_config
from justniffer.settings import settings

counts = 0


@dataclass
class EndpointAddress:
    ip: str
    port: int

    def __to_output_str__(self, *args, **kwargs) -> str:
        return f'{self.ip}:{self.port}'


class TLSConnectionInfoEx(TLSConnectionInfo):

    def __to_output_str__(self, sep: str, null_value: str) -> str:
        return sep.join(map(lambda value: to_str(value, sep=sep, null_value=null_value), (
            self.server_name_list[0] if self.server_name_list else None,
            self.version,
            self.cipher,
            self.common_name,
            self.organization_name,
            self.expires.strftime("%Y-%m-%d %H:%M:%S") if self.expires else None
        )))
        return f'{to_str(self.server_name_list[0] if self.server_name_list else None)} {to_str(self.version)} {to_str(self.cipher)} {to_str(self.common_name)} {to_str(self.organization_name)} {to_str(self.expires.strftime("%Y-%m-%d %H:%M:%S") if self.expires else None)}'


connections: dict[Conn, Connection] = {}


def _get_content(events: Iterable[Event], class_: type) -> bytes:
    return b''.join(map(lambda event: cast(ContentEvent, event).content, filter(lambda event: isinstance(event, class_), events)))


def response(events: Iterable[Event]) -> bytes:
    response = _get_content(events, ResponseEvent)
    return response


def request(events: Iterable[Event]) -> bytes:
    request = _get_content(events, RequestEvent)
    return request


class Extractor(ABC, BaseExtractor):

    @abstractmethod
    def value(self, connection: Connection, events: list[Event], time: float | None) -> ExtractorResponse | None: ...


class RequestSize(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> int | None:
        return len(request(events))


class ResponseSize(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> int | None:
        return len(response(events))


class ConnectionTime(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> float | None:
        opening_ts = None
        open_ts = None
        for event in events:
            if opening_ts is None and isinstance(event, TimedEvent) and event.status is Status.opening:
                opening_ts = event
            if open_ts is None and isinstance(event, TimedEvent) and event.status is Status.open:
                open_ts = event
            if opening_ts and open_ts:
                break
        if open_ts is not None and opening_ts is not None:
            return open_ts.ts - opening_ts.ts
        else:
            return None


class ResponseTime(Extractor):

    def value(self, connection: Connection, events: list[Event], time: float | None) -> float | None:
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
            return first_response.ts - last_request.ts
        else:
            return None


class RequestTime(Extractor):

    def value(self, connection: Connection, events: list[Event], time: float | None) -> float | None:
        last_request = None
        first_request = None
        for event in events:
            if first_request is None and isinstance(event, TimedEvent) and event.status is Status.request:
                first_request = event
            if isinstance(event, TimedEvent) and event.status is Status.request:
                last_request = event
        if last_request is not None and first_request is not None:
            return last_request.ts - first_request.ts
        else:
            return None


MAX_BITS = 2**64


class ConnectionID(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> str:
        pos_hash = hash(connection.id) % (MAX_BITS)
        return hex(pos_hash)[2:].zfill(16)

class CloseOriginator(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> Literal['client', 'server'] | None:
        close_event: CloseEvent | None = cast(CloseEvent, next(filter(lambda event: isinstance(event, CloseEvent) and event.status is Status.close, events), None))
        if close_event is not None:
            source_ip, source_port = connection.conn[0]
            if close_event.source_ip == source_ip and close_event.source_port == source_port:
                return 'client'
            else:
                return 'server'
        else:
            return None


class ConnectionDuration(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> float | None:
        timed_events: list[TimedEvent] = list(filter(lambda event: isinstance(event, TimedEvent), events))  # type: ignore
        if len(timed_events) > 0:
            e = timed_events[-1]
            return e.ts - connection.time
        else:
            return None


class Idle1Time(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> float | None:
        open_time = None
        request_time = None
        for event in events:
            if event.status is Status.open:
                open_time = cast(TimedEvent, event).ts
            if event.status is Status.request and request_time is None:
                request_time = cast(TimedEvent, event).ts
        if open_time is not None and request_time is not None:
            return request_time - open_time
        else:
            return None


class Idle2Time(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> float | None:
        close_time = None
        response_time = None
        for event in events:
            if event.status is Status.response:
                response_time = cast(TimedEvent, event).ts
            if event.status is Status.close:
                close_time = cast(TimedEvent, event).ts
        if close_time is None and time is not None:
            close_time = time
        if close_time is not None and response_time is not None:
            return close_time - response_time
        else:
            return None


class ConnectionRequests(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> int:
        return connection.requests


class ConnectionState(Extractor):
    _state_map = {
        # (open, closed, data): status
        (False, False, False): None,
        (False, True, False): 'refused',
        (False, True, True): 'closed',
        (True, False, False): 'truncated',
        (True, False, True): 'started',
        (True, True, False): 'closed',
        (True, True, True): 'unique',
    }

    def value(self, connection: Connection, events: list[Event], time: float | None) -> str | None:
        is_open = is_closed = has_data = is_truncated = False

        for event in events:
            if isinstance(event, TimedEvent):
                match event.status:
                    case Status.open:
                        is_open = True
                    case Status.close:
                        is_closed = True
                    case Status.request | Status.response:
                        has_data = True
            elif event.status is Status.interrupted:
                is_truncated = True

        if not is_open and not is_closed and has_data:
            return 'truncated' if is_truncated else 'continue'

        return self._state_map.get(
            (is_open, is_closed, has_data),
            None
        )


class RequestTimestamp(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> datetime | None:
        req: TimedEvent | None = cast(TimedEvent, next(filter(lambda event: isinstance(event, TimedEvent) and event.status is Status.request, events), None))
        if req is not None:
            return datetime.fromtimestamp(req.ts)
        else:
            req = cast(TimedEvent, next(filter(lambda event: isinstance(event, TimedEvent), events), None))
            if req is not None:
                return datetime.fromtimestamp(req.ts)
        return None


class PayloadExtractor(ContentExtractor):
    def value(self, connection: Connection, events: list[Event], time: float | None, request: bytes, response: bytes) -> ExtractorResponse | None:
        (source_ip, source_port), (dest_ip, dest_port) = connection.conn
        conn_str = f'{source_ip}-{source_port}-{dest_ip}-{dest_port}'
        req_filename, res_filename = None, None
        tmp_dir = '/tmp'
        if request:
            req_filename = f'{tmp_dir}/conn-{conn_str}-{connection.requests}-request.bin'
            with open(req_filename, 'wb+') as f:
                f.write(request)
        if response:
            res_filename = f'{tmp_dir}/conn-{conn_str}-{connection.requests}-response.bin'
            with open(res_filename, 'wb+') as f:
                f.write(response)
        return req_filename, res_filename


@dataclass
class SSHConnData:
    client_banner: str
    server_banner: str
    cookie: str | None


class SSHInfoExtractor(TypedContentExtractor[SSHConnData]):
    name = 'SSH'  # type: ignore

    def value(self, connection: Connection, events: list[Event], time: float | None, request: bytes, response: bytes) -> ExtractorResponse | None:
        res = self.get_conn_attrs(connection)
        if res is None:
            if response and request:
                res_info = ssh_info(request, response)
                if res_info is not None:
                    res = SSHConnData(res_info.client_banner, res_info.server_banner, res_info.kexinit.cookie if res_info.kexinit is not None else None)
                    self.set_conn_attrs(connection, res)
        elif res.cookie is None:
            kexinit = extract_kexinit_info(response)
            if kexinit is not None:
                res.cookie = kexinit.cookie
        return res


class PlainTextExtractor(ContentExtractor):
    printable = string.digits + string.ascii_letters + string.punctuation + ' '
    name = 'UNKNOWN'  # type: ignore
    _length = 10

    def __init__(self, length: int = 10):
        self._length = length

    def value(self, connection: Connection, events: list[Event], time: float | None, request: bytes, response: bytes) -> ExtractorResponse | None:
        req = None
        res = None
        length = self._length
        if request:
            req = self._sample(request)
        if response:
            res = self._sample(response)
        if req is None and res is None:
            return None
        else:
            return f'{to_str(req)} {to_str(res)}'

    def _sample(self, request: bytes):

        decoded_text = request[:self._length].decode(DEFAULT_CHARSET, errors='ignore')
        cleaned_text = ''.join(c for c in decoded_text if c in self.printable)
        return cleaned_text


class TLSInfoExtractor(TypedContentExtractor[TLSConnectionInfo]):
    name = 'TLS'  # type: ignore

    def value(self, connection: Connection, events: list[Event], time: float | None, request: bytes, response: bytes) -> TLSConnectionInfo | None:
        tls = self.get_conn_attrs(connection)
        if tls is None:
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
                # if version is None:
                #     logger.warning(request)
                #     logger.warning(response)
                # if cipher is None:
                #     logger.warning(request)
                #     logger.warning(response)
                tls = TLSConnectionInfoEx(server_name_list, sid, version, cipher, common_name, organization_name, expires)
                self.set_conn_attrs(connection, tls)
            else:
                if connection.conn[1][1] == 443:
                    logger.warning(request)

        return tls


def get_sni(tls: TLSInfo | None) -> list[str] | None:
    if hasattr(tls, 'messages'):
        msgs = getattr(tls, 'messages', list())
        for msg in msgs:
            name = getattr(msg,  'sni_hostnames', None)
            if name is not None:
                return name
    return None


@dataclass(kw_only=True)
class HttpInfo:
    method: str | None = None
    url: str | None = None
    host: str | None = None
    code: int | None = None
    version: str | None = None
    content_type: str | None = None


class HttpInfoExtractor(ContentExtractor):
    name = 'HTTP'  # type: ignore

    def _get_header(self, headers: dict[str, list[str]], name: str) -> str | None:
        values = headers.get(name)
        if values is not None and len(values) > 0:
            return values[0]
        return None

    def value(self, connection: Connection, events: list[Event], time: float | None, request: bytes, response: bytes) -> HttpInfo | None:
        
        res = parse_http_content(request, response)
        request_obj, response_obj = res
        method = request_obj.method if request_obj else None
        url = request_obj.url if request_obj else None
        host_list = request_obj.headers.get('Host') if request_obj else None
        if host_list is None:
            host_list = [to_str(None)]
        host = host_list[0]
        code = response_obj.code if response_obj else None
        version = response_obj.version if response_obj else None
        if request_obj is None and response_obj is None:
            http_info_old = self.get_conn_attrs(connection)
            if http_info_old is not None:
                return HttpInfo(method='...', url=http_info_old.url, host=http_info_old.host)
            else:
                return None
        else:
            content_type = self._get_header(response_obj.headers, 'Content-Type') if response_obj else None
            http_info = HttpInfo(method=method, url=url, host=host, code=code, version=version, content_type=content_type)
            http_info_old  = self.get_conn_attrs(connection)
            if http_info_old is None:
                self.set_conn_attrs(connection, http_info)
            return http_info


class IPPort(Extractor, ABC):
    index: int

    def value(self, connection: Connection, events: list[Event], time: float | None) -> EndpointAddress:
        ip, port = connection.conn[self.index]
        return EndpointAddress(ip, port)


class DestIPPort(IPPort):
    index = 1


class SourceIPPort(IPPort):
    index = 0


DEFAUL_EXTRACTOR_CLASSES = (RequestTimestamp, ConnectionID, ConnectionState, CloseOriginator, ConnectionRequests,
                            SourceIPPort, DestIPPort,
                            ConnectionTime, RequestTime, ResponseTime, Idle1Time, Idle2Time, ConnectionDuration,
                            RequestSize, ResponseSize, 'ProtocolSelector')


def extractors_classes() -> tuple[ClassDef, ...]:
    config = load_config(settings.config_file)
    return _get_classes_def(config.extractors, DEFAUL_EXTRACTOR_CLASSES)


def _get_classes_def(defs: dict[str, dict | None] | None, default: tuple[ClassDef, ...]) -> tuple[ClassDef, ...]:
    if defs is not None:
        return tuple(map(lambda e: e, defs.items()))
    else:
        return default


DEFAULT_SELECTOR_CLASSES = TLSInfoExtractor, HttpInfoExtractor, SSHInfoExtractor, PlainTextExtractor


def selectors_classes(selectors: dict[str, dict | None] | None = None) -> tuple[ClassDef, ...]:
    return _get_classes_def(selectors, DEFAULT_SELECTOR_CLASSES)


def setup_connection(conn: Conn, time: float) -> Connection:
    connection = connections.get(conn)
    if connection is None:
        connection = Connection(conn=conn, time=time)
        connections[conn] = connection
    logger.debug(f'connections = {len(connections)}')
    return connection


def remove_connection(conn: Conn) -> Connection:
    connection = connections.pop(conn)
    logger.debug(f'connections = {len(connections)}')
    return connection


ExtractorManager = TypedPluginManager[Extractor | ContentExtractor]


ProtocolSelectors = TypedPluginManager[ContentExtractor]


class ProtocolSelector(ContentExtractor):
    _plugin_manager = ProtocolSelectors(__name__)

    _subexector: tuple[ContentExtractor, ...]

    def __init__(self, selectors: dict[str, dict | None] | None = None) -> None:
        self._subexector = self._plugin_manager.get_objects(*selectors_classes(selectors))

    def value(self, connection: Connection, events: list[Event], time: float | None, request: bytes, response: bytes) -> ProtocolInfo | None:
        for e in self._subexector:
            res = e.value(connection, events, time, request, response)
            if res is not None:
                return ProtocolInfo(e.name or '',  res)
        return None


class Exchange(ExchangeBase):
    _events: list[Event]
    _conn: Conn | None
    _extractors: tuple[Extractor | ContentExtractor, ...]
    _formatter = get_formatter()
    _plugin_manager = ExtractorManager(__name__)

    def __init__(self) -> None:
        global counts
        self._extractors = self._plugin_manager.get_objects(*extractors_classes())
        self._events = []
        self._events.append(Event(Status.init))
        counts += 1
        self._conn = None
        logger.debug(f'__init__ {counts=} {id(self)=} ')
        self._connection_to_be_removed = False

    def _setup_conn(self, conn: Conn, time: float) -> Connection | None:
        if self._conn is not None:
            assert self._conn == conn
        else:
            self._conn = conn
            return setup_connection(conn, time)
        return None

    def on_opening(self, conn: Conn, time: float) -> None:
        self._setup_conn(conn, time)
        self._events.append(TimedEvent(Status.opening, time))
        logger.debug(f'on_opening {id(self)=}  {conn=} ')

    def on_open(self, conn: Conn, time) -> None:
        self._setup_conn(conn, time)
        self._events.append(TimedEvent(Status.open, time))
        logger.debug(f'on_open {id(self)=}  {conn} {type(time)}')

    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        self._refresh_conn_last_data(conn, time)
        self._events.append(RequestEvent(content=content, time=time))
        logger.debug(f'on_request {id(self)=} {conn=}')
        logger.debug(repr(content))

    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        self._refresh_conn_last_data(conn, time)
        self._events.append(ResponseEvent(content=content, time=time))
        logger.debug(f'on_response {id(self)=}  {conn=} ')
        logger.debug(repr(content))

    def _refresh_conn_last_data(self, conn: Conn, time: float) -> None:
        self._setup_conn(conn, time)

    def on_close(self, conn: Conn, time: float, source_ip: str, source_port: int) -> None:
        self._setup_conn(conn, time)
        self._refresh_conn_last_data(conn, time)
        self._events.append(CloseEvent(source_ip=source_ip, source_port=source_port, ts=time))
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

    def result(self, time: float | None) -> str | None:
        res = None
        if self._conn is None:
            logger.warning(f'{id(self)=} {counts=} {self._conn=} {self._events}')
        else:
            connection = connections[self._conn]
            if filter(lambda event: isinstance(event, TimedEvent) and event.status is Status.request, self._events):
                connection.requests += 1
            res = self.value(connection, time)
            if self._connection_to_be_removed:
                remove_connection(self._conn)

            # logger.info(f'{id(self)=} {counts=} {self._conn=} {self._events}')
        return str(res)

    def value(self, connection: Connection, time: float | None) -> Any:
        request_ = None
        response_ = None
        values = {}

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
            if isinstance(e, ContentExtractor):
                value = e.value(connection, self._events, time, get_request(), get_response())
            else:
                value = e.value(connection, self._events, time)
            values[e.name] = value

        return self._formatter.format(values)

    def __del__(self) -> None:
        global counts
        counts -= 1
        logger.debug(f'__del__ {counts=} {id(self)=}  ')


class JSONExchange(Exchange):
    _formatter = JSONFormatter()


app = Exchange
