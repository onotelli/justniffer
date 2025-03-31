from datetime import datetime

class Pippo:
    def result(self) -> str:
        return 'ok'
    def on_open(self, conn, time) -> None:
        print('on_open', conn, time)
    def on_opening(self, conn, time) -> None:
        t = datetime.fromtimestamp(time)
        print ('on_opening',   time, conn)

    def on_request(self, conn, content, time) -> None:
        t = datetime.fromtimestamp(time)
        print ('on_request',   time, conn, content[:10])

    def on_close(self, conn, time) -> None:
        print ('on_close',   conn, time)

    def on_response(self, conn, content, t) -> None:
        print ('on_response',   conn, t, content[:10])

def u (*args) -> None:
    print ('fico')
