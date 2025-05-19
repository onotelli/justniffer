
METHODS = [m.encode() for m in ('GET', 'POST', 'PUT', 'PATCH', 
                                'DELETE', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT')]

class Exchange:
    _response: bytes| None
    def __init__(self) -> None:
        self._request = b''
        self._response = None

    def on_request(self, conn, content: bytes, time: float) -> None:
        self._request+=content

    def on_response(self, conn, content: bytes, time: float) -> None:
        if self._response is None: 
            self._response = content 

    def result(self, time:float | None) -> str | None:
        for m in METHODS:
            if self._request.startswith(m):
                line = self._request.decode(errors='ignore').split('\r')[0]
                if self._response is not None:
                    line += ' | ' + (str(self._response.decode(errors='ignore').splitlines()[0]))
                print(line)
        return None
    

app = Exchange
