import os

from datetime import datetime
class Test:
    def __init__(self):
        pass

    def __call__(self, test:bytes):
        try:
            # get first line in optimized way
            first_line = test[:1024].split(b'\n')[0]
            t, source, dest = first_line.decode().split()
            d = datetime.fromtimestamp(float(t))
            print (f'{os.getuid()} {d} {source} {dest}')
        except KeyboardInterrupt:
            raise
        except:
            pass

app = Test()
print(os.getuid())