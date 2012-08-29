#ifndef _sniffer_python_embedding_h
#define _sniffer_python_embedding_h

#include <boost/python.hpp>
#include "formatter.h"

namespace python=boost::python;

class OUTStream
{
public:
  virtual void write(string val){
    cout << val;
  }
  
};

class TCPStream
{
public:
    TCPStream()
    {
        _tcp_stream=0;
    }
    
    TCPStream(tcp_stream* stream )
    {
        _tcp_stream=stream;
    }
    
    std::string src_ip(){
        return ip_to_str(_tcp_stream->addr.saddr);
    }
    
    std::string dst_ip(){
        return ip_to_str(_tcp_stream->addr.daddr);
    }
    
    int dst_port(){
        return _tcp_stream->addr.dest;
    }
    
    int src_port(){
        return _tcp_stream->addr.source;
    }
    
    //virtual ~TCPStream(){}
private:
    tcp_stream * _tcp_stream;
};



class BaseHandler: public basic_handler, public boost::noncopyable
{
public:
    //virtual void append(int i) = 0;
    virtual void append(OUTStream& s) = 0;
	virtual void onOpening(tcp_stream* pstream, const timeval* t){
	    TCPStream stream(pstream);
	    onOpening(stream, 0.0);
	}
	virtual void onOpening(TCPStream& stream, double time)=0;
	/*virtual void append(std::basic_ostream<char>& out, const timeval* t) {}
	virtual void onOpening(tcp_stream* pstream, const timeval* t){}
	virtual void onOpen(tcp_stream* pstream, const timeval* t){}
	virtual void onRequest(tcp_stream* pstream, const timeval* t){}
	virtual void onResponse(tcp_stream* pstream,const  timeval* t){}
	virtual void onClose(tcp_stream* pstream, const timeval* ,unsigned char* packet){}
	*/
    virtual ~BaseHandler() {};
}; 

#endif// _sniffer_python_embedding_h
