from unittest.mock import Mock
from dataclasses import dataclass

from httptools.parser.parser import HttpRequestParser, HttpResponseParser
DEFAULT_CHARSET='utf-8'

class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)


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
        self.headers = CaseInsensitiveDict()
        self.version = ''
        self.content = b''

    def on_body(self, content: bytes) -> None:
        self.content = content

    def on_header(self, name: bytes, value: bytes) -> None:
        name_ = name.decode(DEFAULT_CHARSET)
        value_ = value.decode(DEFAULT_CHARSET)
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
        self.url = url.decode(DEFAULT_CHARSET)


class ResProtocol(BaseProtocol, HttpResponse):
    message: str

    def on_status(self, message: bytes) -> None:
        self.message = message.decode(DEFAULT_CHARSET)

    def __init__(self) -> None:
        super().__init__()
        self.url = ''


def parse_http_content(request: bytes, response: bytes) -> tuple[HttpRequest | None, HttpResponse | None]:
    req: ReqProtocol | None = ReqProtocol()
    resp: ResProtocol | None = ResProtocol()
    request_parser = HttpRequestParser(req)
    try:
        request_parser.feed_data(request)
    except:
        pass
    response_parser = HttpResponseParser(resp)
    try:
        response_parser.feed_data(response)
    except:
        pass
    req.method = request_parser.get_method().decode(DEFAULT_CHARSET)  # type: ignore
    resp.code = response_parser.get_status_code()  # type: ignore
    req_version = request_parser.get_http_version()
    resp_version = response_parser.get_http_version()
    req.version =  req_version  # type: ignore
    resp.version =  resp_version # type: ignore 
    if  req_version == '0.0':
        req = None
    if resp_version == '0.0':
        resp = None
    return req, resp
