import os

from datetime import datetime
from logging import basicConfig, DEBUG, debug, info
basicConfig(level=DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Test:
    def __init__(self):
        self._methods = (b'GET', b'POST', b'HEAD', b'PUT', b'DELETE')

    def __call__(self, test:bytes):
        try:
            # get first line in optimized way
            pos = test.find(b'\n')
            if pos != -1:
                first_line_bytes = test[:pos]
                rest = test[pos +2:]            
                t, source, dest = first_line_bytes.decode().split()
                d = datetime.fromtimestamp(float(t))
                print (f'{os.getuid()} {d} {source} {dest}')
                if rest.startswith(self._methods):
                    print(rest.decode())
                else:
                    print(f'**** {str(rest[:10])}')

        except KeyboardInterrupt:
            raise
        except:

            pass

app = Test()
