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

    def result(self, time: float) -> str | None:
        pass
