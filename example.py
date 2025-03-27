
class Test:
    def __init__(self):
        pass

    def __call__(self, test:bytes):
        print (test.decode(errors='ignore'))


app = Test()
