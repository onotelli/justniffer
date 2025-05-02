
METHODS = [m.encode() for m in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT')]

class Exchange:
    def __init__(self) -> None:
        self._request = b''
    
    def on_request(self, conn, content: bytes, time: float) -> None:
        self._request+=content


    def result(self) -> str | None:
        for m in METHODS:
            if self._request.startswith(m):
                print(self._request.decode(errors='ignore').split('\n')[0])
                break
        return None
    

app = Exchange
