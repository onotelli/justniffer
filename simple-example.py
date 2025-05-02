def app(log:bytes):
    print(log.decode('utf-8', errors='ignore').split())


def test2(log:bytes):
    print(list(reversed(log.decode('utf-8', errors='ignore').split())))