import sys
from enum import Enum, auto
from loguru import logger
from dataclasses import dataclass
from justniffer.model import Conn

logger.remove()

CONNECTION_TIMEOUT = 5
logger.add(sys.stderr)

METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT')
counts = 0


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
    ts: float | None = None


class Exchange:
    _events: list[Event]
    _conn: Conn | None 

    def __init__(self) -> None:
        global counts
        self._events = []
        self._events.append(Event(Status.init))
        counts += 1
        self._conn = None
        logger.debug(f'__init__ {counts=} {id(self)=} ')

    def _setup_conn(self, conn: Conn) -> None:
        if self._conn is not None:
            assert self._conn == conn
        else:
            self._conn = conn

    def on_opening(self, conn: Conn, time: float) -> None:
        self._setup_conn(conn)
        self._events.append(Event(Status.opening, time))
        logger.debug(f'on_opening {id(self)=}  {conn=} ')

    def on_open(self, conn: Conn, time) -> None:
        self._setup_conn(conn)
        self._events.append(Event(Status.open, time))
        logger.debug(f'on_open {id(self)=}  {conn} {type(time)}')

    def on_request(self, conn: Conn, bytes, time: float) -> None:
        self._setup_conn(conn)
        self._events.append(Event(Status.request, time))
        logger.debug(f'on_request {id(self)=}  {conn=}')

    def on_response(self, conn: Conn, bytes: bytes, time: float) -> None:
        self._setup_conn(conn)
        self._events.append(Event(Status.response, time))
        logger.debug(f'on_response {id(self)=}  {conn=} ')

    def on_close(self, conn: Conn, time: float) -> None:
        self._setup_conn(conn)
        self._events.append(Event(Status.close, time))
        logger.debug(f'on_close {id(self)=}  {conn=} ')

    def on_interrupted(self) -> None:
        self._events.append(Event(Status.interrupted))
        logger.debug(f'on_interrupted  {id(self)=} ')

    def on_timed_out(self, conn: Conn, time: float) -> None:
        self._events.append(Event(Status.timed_out, time))
        logger.debug(f'on_timed_out  {id(self)=} {conn=} ')

    def result(self) -> str | None:
        logger.info(f'{id(self)=} {counts=} {self._conn=} {self._events}')
        return None

    def __del__(self) -> None:
        global counts
        counts -= 1
        logger.debug(f'__del__ {counts=} {id(self)=}  ')


app = Exchange
