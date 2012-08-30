/*
	Copyright (c) 2007-2012 Plecno s.r.l. All Rights Reserved 
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>	

*/

#ifndef _sniffer_python_embedding_h
#define _sniffer_python_embedding_h

#include <boost/python.hpp>
#include "formatter.h"

namespace python=boost::python;

class OUTStream
{
public:
  OUTStream(std::basic_ostream<char>& out):_out(out){};
  virtual void write(string val){
    _out << val;
  }
private:
    std::basic_ostream<char>& _out;
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
    
    std::string client_data(){
        return std::string(_tcp_stream->server.data, _tcp_stream->server.data + _tcp_stream->server.count_new);
    }
    
    std::string server_data(){
        return std::string(_tcp_stream->client.data, _tcp_stream->client.data + _tcp_stream->client.count_new);
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

class BaseHandlerInterface
{
public:
    virtual void append(OUTStream& s, double time){};
	virtual void onOpening(TCPStream& stream, double time){};
	virtual void onOpen(TCPStream& stream, double time){};
	virtual void onRequest(TCPStream& stream, double time){};
	virtual void onResponse(TCPStream& stream, double time){};
	virtual void onClose(TCPStream& stream, double time){};
};

class BaseHandler: public basic_handler, public BaseHandlerInterface, public boost::noncopyable
{
public:
    //virtual void append(int i) = 0;
	virtual void append(std::basic_ostream<char>& out, const timeval* t){
        OUTStream s = OUTStream(out);
	    append(s, to_double(*t));
	}
    
	virtual void onOpening(tcp_stream* pstream, const timeval* t){
	    onOpening(get_tcp_stream(pstream), to_double(*t));
	}
    
	virtual void onOpen(tcp_stream* pstream, const timeval* t){
	    onOpen(get_tcp_stream(pstream), to_double(*t));
	}
    
	virtual void onRequest(tcp_stream* pstream, const timeval* t){
	    onRequest(get_tcp_stream(pstream), to_double(*t));
	}
    
	virtual void onResponse(tcp_stream* pstream,const  timeval* t){
	    onResponse(get_tcp_stream(pstream), to_double(*t));
	}
    
	virtual void onClose(tcp_stream* pstream, const timeval* t ,unsigned char* packet){
	    onClose(get_tcp_stream(pstream), to_double(*t));
	}
    virtual void append(OUTStream& s, double time){};
	virtual void onOpening(TCPStream& stream, double time){};
	virtual void onOpen(TCPStream& stream, double time){};
	virtual void onRequest(TCPStream& stream, double time){};
	virtual void onResponse(TCPStream& stream, double time){};
	virtual void onClose(TCPStream& stream, double time){};

	/*virtual void append(std::basic_ostream<char>& out, const timeval* t) {}
	virtual void onOpening(tcp_stream* pstream, const timeval* t){}
	virtual void onOpen(tcp_stream* pstream, const timeval* t){}
	virtual void onRequest(tcp_stream* pstream, const timeval* t){}
	virtual void onResponse(tcp_stream* pstream,const  timeval* t){}
	virtual void onClose(tcp_stream* pstream, const timeval* ,unsigned char* packet){}
	*/
    virtual ~BaseHandler() {
        
    };
private:
    TCPStream& get_tcp_stream(tcp_stream* pstream)
    {
        if (!pTcpstream)
            pTcpstream = boost::shared_ptr<TCPStream>(new TCPStream(pstream));
        return *pTcpstream.get();
    }
        
    boost::shared_ptr<TCPStream> pTcpstream;
}; 

class python_handler: public basic_handler
{
public:
    python_handler(const string& python_ref);
    virtual void append(std::basic_ostream<char>& out, const timeval* t);
	virtual void onOpening(tcp_stream* pstream, const timeval* t);
	virtual void onOpen(tcp_stream* pstream, const timeval* t);
	virtual void onRequest(tcp_stream* pstream, const timeval* t);
	virtual void onResponse(tcp_stream* pstream,const  timeval* t);
	virtual void onClose(tcp_stream* pstream, const timeval* ,unsigned char* packet);
    virtual ~python_handler(){};
private:
    BaseHandler* __handler;
    python::object py_base;
};

#endif// _sniffer_python_embedding_h
