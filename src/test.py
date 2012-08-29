import justniffer

def pippo():
    print "pippo"
    
    
class PythonDerived(justniffer.BaseHandler):
    def append(self, s):
        s.write("pippO")
        
