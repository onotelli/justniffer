#include "test.h"
#include <iostream>
#include "utilities.h"


/**

struct tcp_stream {
            struct tuple4 {
                 u_short source;
                 u_short   dest;
                 u_int     saddr;
                 u_int     daddr;
            } addr;
            char           nids_state;
            struct half_stream {
                 char state;
                 char collect;
                 char collect_urg;
                 char *data;
                 u_char    urgdata;
                 int  count;
                 int  offset;
                 int  count_new;
                 char count_new_urg;
                 ...
            } client;
            struct half_stream  server;
            ...
            void           *user;
       };


**/


class BaseHandlerWrap: public BaseHandler, public python::wrapper<BaseHandler>
{
public:
    virtual void append(OUTStream& s) {
        this->get_override("append")(boost::ref(s));
    };
	virtual void onOpening(TCPStream& stream, double time){
	    this->get_override("onOpening")(boost::ref(stream), time);
    }
}; 


// Pack the Base class wrapper into a module
BOOST_PYTHON_MODULE(justniffer)
{
  python::class_<BaseHandlerWrap, boost::noncopyable> basehandler("BaseHandler");
  python::class_<TCPStream, boost::noncopyable> stream("TCPStream");
  python::class_<OUTStream, boost::noncopyable> out("OUTStream");
  stream.def("src_port", &TCPStream::src_port).def("dst_port", &TCPStream::dst_port).def("src_ip", &TCPStream::src_ip).def("dst_ip", &TCPStream::dst_ip);
  out.def("write", &OUTStream::write);
  
}

const char * test_file ="test.py";

const char* class_name = "PythonDerived";

using namespace std;

int main_()
{
    Py_Initialize();
    // Register the module with the interpreter
      if (PyImport_AppendInittab("justniffer", initjustniffer) == -1)
        throw std::runtime_error("Failed to add embedded_hello to the interpreter's "
                     "builtin modules");

      
      // Retrieve the main module
      python::object main = python::import("__main__");
      
      // Retrieve the main module's namespace
      python::object global(main.attr("__dict__"));

      // Define the derived class in Python.
      try{
          python::object result = python::exec_file(test_file, global, global);
          python::object PythonDerived = global[class_name];

          
          // But now creating and using instances of the Python class is almost
          // as easy!
          python::object py_base = PythonDerived();
          BaseHandler& py = python::extract<BaseHandler&>(py_base) BOOST_EXTRACT_WORKAROUND;
          OUTStream s = OUTStream();
          // Make sure the right 'hello' method is called.
         py.onOpening((tcp_stream*) 0, (timeval*)0) ;
         py.append(boost::ref(s)) ;
         cout << endl;
      }
      catch (python::error_already_set& e)
      {
        PyErr_Print();
        return -1;
      }

 }
