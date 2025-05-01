from unittest.mock import Mock
from dataclasses import dataclass

from httptools.parser.parser import HttpRequestParser, HttpResponseParser


@dataclass
class HttpMessage:
    version: str
    headers: dict[str, list[str]]
    content: bytes


@dataclass
class HttpRequest(HttpMessage):
    method: str
    url: str


@dataclass
class HttpResponse(HttpMessage):
    code: int
    message: str


class BaseProtocol:
    headers: dict[str, list[str]]
    version: str
    content: bytes

    def __init__(self) -> None:
        self.headers = {}
        self.version = ''
        self.content = b''

    def on_body(self, content: bytes) -> None:
        self.content = content

    def on_header(self, name: bytes, value: bytes) -> None:
        name_ = name.decode('utf-8')
        value_ = value.decode('utf-8')
        if name_ in self.headers:
            self.headers[name_].append(value_)
        else:
            self.headers[name_] = [value_]


class ReqProtocol(BaseProtocol, HttpRequest):
    url: str

    def __init__(self) -> None:
        super().__init__()
        self.method = 'GET'
        self.url = ''

    def on_url(self, url: bytes) -> None:
        self.url = url.decode('utf-8')


class ResProtocol(BaseProtocol, HttpResponse):
    message: str

    def on_status(self, message: bytes) -> None:
        self.message = message.decode('utf-8')

    def __init__(self) -> None:
        super().__init__()
        self.url = ''


def parse_http_content(request: bytes, response: bytes) -> tuple[HttpRequest | None, HttpResponse | None]:
    req: ReqProtocol | None = ReqProtocol()
    resp: ResProtocol | None = ResProtocol()
    request_parser = HttpRequestParser(req)
    request_parser.feed_data(request)
    response_parser = HttpResponseParser(resp)
    response_parser.feed_data(response)
    req.method = request_parser.get_method().decode('utf-8')  # type: ignore
    resp.code = response_parser.get_status_code()  # type: ignore
    if response_parser.get_http_version() == '0.0':
        req = None
    if request_parser.get_http_version() == '0.0':
        resp = None
    return req, resp
