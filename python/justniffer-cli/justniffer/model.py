from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import cast, Any
from time import time



Endpoint = tuple[str, int]
Conn = tuple[Endpoint, Endpoint]


class ExchangeBase:

    def on_opening(self, conn: Conn, time: float) -> None:
        pass

    def on_open(self, conn: Conn, time) -> None:
        pass

    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        pass

    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        pass

    def on_close(self, conn: Conn, time: float, source_ip: str, source_port: int) -> None:
        pass

    def on_interrupted(self) -> None:
        pass

    def on_timed_out(self, conn: Conn, time: float) -> None:
        pass

    def result(self, time: float | None) -> str | None:
        pass


class TLSVersion(Enum):
    TLS_1_3 = 772
    TLS_1_2 = 771
    TLS_1_1 = 770
    TLS_1_0 = 769
    SSL_3_0 = 768
    GREASE = -1

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_int(cls, value: int | None) -> 'TLSVersion| None':
        if value is None:
            return None
        else:
            return cast(TLSVersion, cls._value2member_map_.get(value, cls.GREASE))


@dataclass
class TLSConnectionInfo:
    server_name_list: list[str] | None
    sid: bytes
    version: TLSVersion | None
    cipher: str | None
    common_name: str | None
    organization_name: str | None
    expires: datetime | None


@dataclass
class Connection:
    conn: Conn
    time: float
    requests: int = 0
    protocol: dict[str, Any] = field(default_factory=dict)
    start : float = field(default_factory=lambda: time())     

    @property
    def id(self) -> str:
        return hex(hash(id(self)+self.start))


ExtractorResponse = Any


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
class CloseEvent(TimedEvent):
    source_ip: str
    source_port: int

    def __init__(self, ts: float, source_ip: str, source_port: int) -> None:
        super().__init__(ts=ts, status=Status.close)
        self.source_ip = source_ip
        self.source_port = source_port


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


@dataclass
class ProtocolInfo:
    name: str
    info: Any
