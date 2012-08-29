import justniffer

def pippo():
    print "pippo"
    
    
class PythonDerived(justniffer.BaseHandler):
    def append(self, s):
        s.write("pippO")
    def onOpening(self, tcp, time):
        print "onOpening", tcp.dst_port, time
