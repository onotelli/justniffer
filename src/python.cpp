/*
	Copyright (c) 2007-2012 Plecno s.r.l. All Rights Reserved 
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>	
*/

#include "python.h"
#include <iostream>
#include "utilities.h"
#include <map>

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

class python_error : public std::exception
{
public :
    python_error(python::error_already_set& e)
    {
    }
    virtual const char* what () const throw()
    {
        return "Python error\n";
    }
    
};

#define START_PYTHON_CALL try{

#define END_PYTHON_CALL }catch(python::error_already_set& e){PyErr_Print();throw python_error(e);}
class BaseHandlerWrap: public BaseHandler, public python::wrapper<BaseHandler>
{
public:
    virtual void append(OUTStream& s, double time){
        START_PYTHON_CALL
        if (python::override f = this->get_override("append"))
            f(boost::ref(s), time);
        else
            BaseHandler::append(boost::ref(s), time);
        END_PYTHON_CALL
    };

	virtual void onOpening(TCPStream& stream, double time){
        START_PYTHON_CALL
        if (python::override f = this->get_override("onOpening"))
            f(boost::ref(stream), time);
        else
            BaseHandler::onOpening(boost::ref(stream), time);
        END_PYTHON_CALL
    }
    
	virtual void onOpen(TCPStream& stream, double time){
        START_PYTHON_CALL
        if (python::override f = this->get_override("onOpen"))
            f(boost::ref(stream), time);
        else
            BaseHandler::onOpen(boost::ref(stream), time);
        END_PYTHON_CALL
    }
    
	virtual void onRequest(TCPStream& stream, double time){
        START_PYTHON_CALL
        if (python::override f = this->get_override("onRequest"))
            f(boost::ref(stream), time);
        else
            BaseHandler::onRequest(boost::ref(stream), time);
        END_PYTHON_CALL
    }
    
	virtual void onResponse(TCPStream& stream, double time){
        START_PYTHON_CALL
        if (python::override f = this->get_override("onResponse"))
            f(boost::ref(stream), time);
        else
            BaseHandler::onResponse(boost::ref(stream), time);
        END_PYTHON_CALL
    }
    
	virtual void onClose(TCPStream& stream, double time){
        START_PYTHON_CALL
        if (python::override f = this->get_override("onClose"))
            f(boost::ref(stream), time);
        else
            BaseHandler::onClose(boost::ref(stream), time);
        END_PYTHON_CALL
    }
    
	virtual void onExit(TCPStream& stream){
        START_PYTHON_CALL
        if (python::override f = this->get_override("onExit"))
            f(boost::ref(stream));
        else
            BaseHandler::onExit(boost::ref(stream));
        END_PYTHON_CALL
    }
}; 

void read_file(string filename, string capture_string)
{
} 

BOOST_PYTHON_MODULE(justniffer)
{
  python::def("read_file", read_file);
  python::class_<BaseHandlerWrap, boost::noncopyable> basehandler("BaseHandler");
  python::class_<TCPStream, boost::noncopyable> stream("TCPStream", python::no_init);
  python::class_<OUTStream, boost::noncopyable> out("OUTStream", python::no_init);
  
  basehandler.def("onOpen", &BaseHandlerInterface::onOpen)
        .def("onOpening", &BaseHandlerInterface::onOpening)
        .def("onRequest", &BaseHandlerInterface::onRequest)
        .def("onResponse", &BaseHandlerInterface::onResponse)
        .def("onClose", &BaseHandlerInterface::onClose)
        .def("onExit", &BaseHandlerInterface::onExit)
        .def("append", &BaseHandlerInterface::append);
  
  stream.add_property("src_port", &TCPStream::src_port)
        .add_property("dst_port", &TCPStream::dst_port)
        .add_property("src_ip", &TCPStream::src_ip)
        .add_property("dst_ip", &TCPStream::dst_ip)
        .add_property("server_data", &TCPStream::server_data)
        .add_property("client_data", &TCPStream::client_data);

  out.def("write", &OUTStream::write);
}


//class BaseHandlerWrap

const char* class_name = "PythonDerived";
static map<std::string, python::object> classes;
static map<std::string, python::object> filenames;

static bool _inited_python(false);
void InitPython()
{
    if (!_inited_python)
    {
        Py_Initialize();
        // Register the module with the interpreter
        if (PyImport_AppendInittab("justniffer", initjustniffer) == -1)
            throw std::runtime_error("Failed to add embedded_hello to the interpreter's "
                         "builtin modules");
        _inited_python= true;
    }
}

static python::object exit_handler;

python::object get_python_class(const std::string& filename, const std::string& classname)
{
    START_PYTHON_CALL
    std::string key (filename+std::string("#")+classname);
    if (!classes.count(key))
    {
        if (!filenames.count(filename))
        {
            python::object main = python::import("__main__");
            python::dict global(main.attr("__dict__"));
            python::object result = python::exec_file(filename.c_str(), global, global);
            filenames[filename] = global;
            
        }
        python::dict global(filenames[filename]);
        python::object py_base_class = global[classname];
        classes[key]=py_base_class;
        if (global.has_key("on_exit"))
            exit_handler = global["on_exit"];
    }
    return classes[key];
    END_PYTHON_CALL
}

//class python_handler

python_handler::python_handler(const string& python_ref)
{
    START_PYTHON_CALL
    InitPython();
    std::stringstream ss(python_ref);
    std::string filename, classname;
    std::getline( ss, filename, '#' );
    std::getline( ss, classname, '#' );
    python::object  py_base_class = get_python_class(filename, classname);
    py_base= py_base_class();
    BaseHandler& py = python::extract<BaseHandler&>(py_base) BOOST_EXTRACT_WORKAROUND;
    __handler = &py;
    END_PYTHON_CALL
}

void python_handler::append(std::basic_ostream<char>& out, const timeval* t)
{
    __handler->append(out, t);
}

void python_handler::onOpening(tcp_stream* pstream, const timeval* t)
{
    __handler->onOpening(pstream, t);
}

void python_handler::onOpen(tcp_stream* pstream, const timeval* t)
{
    __handler->onOpen(pstream, t);
}

void python_handler::onRequest(tcp_stream* pstream, const timeval* t)
{
    __handler->onRequest(pstream, t);
}

void python_handler::onResponse(tcp_stream* pstream,const  timeval* t)
{
    __handler->onResponse(pstream, t);
}

void python_handler::onClose(tcp_stream* pstream, const timeval*t ,unsigned char* packet)
{
    __handler->onClose(pstream, t, packet);
}

void python_handler::onExit(tcp_stream* pstream)
{
    __handler->onExit(pstream);
}

class PythonModule: public Module
{
public:
    virtual void init(parser* p) { 
        p->add_parse_element("python", pelem(new keyword_params<handler_factory_t_arg<string, python_handler> >()));
    }
    virtual void on_exit(void)
    {
        if (!exit_handler.is_none())
            exit_handler();
    }
};

REGISTER_MODULE(PythonModule);
