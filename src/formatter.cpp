/*
	Copyright (c) 2007 Plecno s.r.l. All Rights Reserved 
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>	
*/

#include "formatter.h"
#include <iostream>
#include <sstream>
#include <map>
#include "regex.h"
#include <cstdio>
#include <ext/stdio_filebuf.h>
#include <signal.h>

using namespace std;

parser* parser::theOnlyParser= NULL;
const char parser::_key_word_id='%';

void parser::nids_handler(struct tcp_stream *ts, void **yoda, struct timeval* t, unsigned char* packet)
{
	check(theOnlyParser != NULL, parser_not_initialized());
	//string flag ="";
	//if (packet)
	//{
    //    flag = "packet found";
	//}
	//cout << "ts->nids_state "<< (int) ts->nids_state << " " <<flag <<"\n";
	
	switch (ts->nids_state) 
	{
		case NIDS_JUST_EST:
			ts->server.collect = 1;
			ts->client.collect = 1;
			theOnlyParser->process_open_connection(ts, t, packet);
			break;
			
		case NIDS_DATA:
			if (ts->server.count_new)
			{
				theOnlyParser->process_client(ts, t, packet);
			}
			if (ts->client.count_new)
			{
				theOnlyParser->process_server(ts, t, packet);
			}
			break;
		case NIDS_EXITING:
		    break;	
		case NIDS_OPENING:
			theOnlyParser->process_opening_connection(ts, t, packet);
			break;
		default:
			theOnlyParser->process_close_connection(ts, t, packet);
			break;
	}
	//cout << "nids_handler end "<< (int)ts->nids_state << "\n";
}


const char* parser::_parse_element(const char* input)
{
	init_parse_elements();
	const char* new_pos = input;
	for (parse_elements::iterator it = elements.begin(); it!= elements.end(); it++)
	{
		new_pos  = (*it).second->parse(input, (*it).first, factories);
		if (new_pos != input) break;
	}
	if (new_pos == input)
	{
		string s(input);
		string::size_type pos = s.find_first_of(" ");
		string::size_type pos2 = s.find_first_of("(");
		if (pos!= s.npos)
		{
			if (pos2 != s.npos)
				pos = min(pos, pos2);
			throw unknown_keyword(string (input , input + pos));
		}
		else
			throw unknown_keyword(string (input));
	}
	return new_pos;
}

void parser::parse(const char* input)
{
	const char* cursor = input;
	string w;
	for (; *cursor != 0;)
	{
		switch (*cursor)
		{
			case _key_word_id:
				if (w.size())
				{
					factories.push_back(handler_factory::ptr(new string_handler_factory(w)));
					w = "";
				}
				cursor = _parse_element(cursor);
				if ((*cursor) == 0) break;
				continue;
			default:
				w+=*cursor;
				break;
		}
		if ((*cursor) == 0) break;
		++cursor;
	}
	if (w.size())
	{
		factories.push_back(handler_factory::ptr( new string_handler_factory(w)));
		w = "";
	}
}

typedef keyword_arg_and_optional_not_found<header_handler_factory_t<regex_handler_request> > req_header;
typedef keyword_arg_and_optional_not_found<header_handler_factory_t<regex_handler_response> > resp_header;
typedef parse_element::ptr pelem;

#define REQUEST_HEADER(key,head) elements[key]=pelem(new req_header(string(head),_default_not_found))
#define RESPONSE_HEADER(key,head) elements[key]=pelem(new resp_header(string(head),_default_not_found))
   
void parser::init_parse_elements()
{
    if (_already_init) return;
    elements["dest.ip"] = pelem(new keyword<handler_factory_t<dest_ip> >());
    elements["source.ip"] = pelem(new keyword<handler_factory_t<source_ip> >());
    elements["dest.port"] = pelem(new keyword<handler_factory_t<dest_port> >());
    elements["source.port"] = pelem(new keyword<handler_factory_t<source_port> >());

    elements["connection"] = pelem(new keyword<handler_factory_t<connection_handler> >());
    elements["connection.time"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, connection_time_handler> >(_default_not_found));
    elements["connection.timestamp"] = pelem(new keyword_arg_and_optional_params<handler_factory_t_arg2<string, string, connection_timestamp_handler> > (string("%D %T"), string( _default_not_found)));
    elements["connection.timestamp2"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, connection_timestamp_handler2> > (_default_not_found));
    elements["close.time"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, close_time> >(_default_not_found));
    elements["close.originator"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, close_originator> >(_default_not_found));
    elements["close.timestamp"] = pelem(new keyword_arg_and_optional_params<handler_factory_t_arg2<string, string, close_timestamp_handler> > ("%D %T", _default_not_found));
    elements["close.timestamp2"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, close_timestamp_handler2> > (_default_not_found));
    elements["request"] = pelem(new keyword_arg<string, regex_handler_factory_t<regex_handler_all_request> >(string(".*")));
    elements["request.timestamp"] = pelem(new keyword_arg_and_optional_params<handler_factory_t_arg2<string, string, request_timestamp_handler> > ("%D %T", _default_not_found));
    elements["request.timestamp2"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, request_timestamp_handler2> > (_default_not_found));
    elements["request.time"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, request_time_handler> >(_default_not_found));
    elements["request.size"] = pelem(new keyword<handler_factory_t<request_size_handler> > ());
    elements["request.line"] = pelem(new keyword<handler_factory_t<request_first_line> >());
    elements["request.method"] = pelem(new keyword_arg_and_optional_params<regex_handler_factory_t<regex_handler_request_line> >(string("(^[^\\s]*)"),_default_not_found ));
    elements["request.url"] = pelem(new keyword_arg_and_optional_params<regex_handler_factory_t<regex_handler_request_line> >(string("^[^\\s]*\\s*([^\\s]*)"),_default_not_found ));
    elements["request.protocol"] = pelem(new keyword_arg_and_optional_params<regex_handler_factory_t<regex_handler_request_line> >(string("^[^\\s]*\\s*[^\\s]*\\s*([^\\s]*)"),_default_not_found ));
    elements["request.grep"] = pelem(new keyword_params_and_arg<regex_handler_factory_t<regex_handler_all_request> >(_default_not_found));
    elements["request.header"] = pelem(new keyword_arg<string, regex_handler_factory_t<regex_handler_request> >(string(".*")));
    
    elements["request.part"] = pelem(new keyword_params<handler_factory_t_arg<string, request_part> >());
    
    elements["session.time"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, session_time_handler> >(_default_not_found));
    elements["session.requests"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, session_request_counter> >(_default_not_found));
    
    REQUEST_HEADER("request.header.host","Host");
    REQUEST_HEADER("request.header.user-agent","User-Agent");
    REQUEST_HEADER("request.header.accept","Accept");
    REQUEST_HEADER("request.header.accept-charset","Accept-Charset");
    REQUEST_HEADER("request.header.accept-encoding","Accept-Encoding");
    REQUEST_HEADER("request.header.accept-language","Accept-Language");
    REQUEST_HEADER("request.header.authorization","Authorization");
    REQUEST_HEADER("request.header.keep-alive","Keep-Alive");
    REQUEST_HEADER("request.header.referer","Referer");
    REQUEST_HEADER("request.header.range","Range");
    REQUEST_HEADER("request.header.cookie","Cookie");
    REQUEST_HEADER("request.header.connection","Connection");
    REQUEST_HEADER("request.header.content-encoding","Content-Encoding");
    REQUEST_HEADER("request.header.content-language","Content-Language");
    REQUEST_HEADER("request.header.transfer-encoding","Transfer-Encoding");
    REQUEST_HEADER("request.header.content-length","Content-Length");
    REQUEST_HEADER("request.header.content-md5","Content-MD5");
    REQUEST_HEADER("request.header.via","Via");
    elements["request.header.value"] = pelem(new keyword_params<header_handler_factory_t<regex_handler_request> >());
    elements["request.header.grep"] = pelem(new keyword_params_and_arg<regex_handler_factory_t<regex_handler_request> >(_default_not_found));

    elements["response"] = pelem(new keyword_arg<string, regex_handler_factory_t<regex_handler_all_response> >(string(".*")));
    elements["response.timestamp"] = pelem(new keyword_arg_and_optional_params<handler_factory_t_arg2<string, string, response_timestamp_handler> > ("%D %T", _default_not_found));
    elements["response.timestamp2"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, response_timestamp_handler2> > ( _default_not_found));
    elements["response.size"] = pelem(new keyword<handler_factory_t<response_size_handler> > ());
    elements["response.time"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, response_time_handler> >(_default_not_found));
    elements["response.time.begin"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, response_time_1> >(_default_not_found));
    elements["response.time.end"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, response_time_2> >(_default_not_found));
    elements["response.line"] = pelem(new keyword<handler_factory_t<response_first_line> >());
    elements["response.protocol"] = pelem(new keyword_arg_and_optional_params<regex_handler_factory_t<regex_handler_response_line> >(string("(^[^\\s]*)"),_default_not_found ));
    elements["response.code"] = pelem(new keyword_arg_and_optional_params<regex_handler_factory_t<regex_handler_response_line> >(string("^[^\\s]*\\s*([^\\s]*)"), _default_not_found));
    elements["response.message"] = pelem(new keyword_arg_and_optional_params<regex_handler_factory_t<regex_handler_response_line> >(string("^[^\\s]*\\s*[^\\s]*\\s*([^\\r]*)"), _default_not_found));
    elements["response.grep"] = pelem(new keyword_params_and_arg<regex_handler_factory_t<regex_handler_all_response> >(_default_not_found));
    elements["response.header"] = pelem(new keyword_arg<string, regex_handler_factory_t<regex_handler_response> >(string(".*")));
    RESPONSE_HEADER("response.header.allow","Allow");
    RESPONSE_HEADER("response.header.server","Server");
    RESPONSE_HEADER("response.header.date","Date");
    RESPONSE_HEADER("response.header.cache-control","Cache-Control");
    RESPONSE_HEADER("response.header.keep-alive","Keep-Alive");
    RESPONSE_HEADER("response.header.connection","Connection");
    RESPONSE_HEADER("response.header.expires","Expires");
    RESPONSE_HEADER("response.header.content-encoding","Content-Encoding");
    RESPONSE_HEADER("response.header.content-language","Content-Laguage");
    RESPONSE_HEADER("response.header.content-length", "Content-Length");
    RESPONSE_HEADER("response.header.content-md5","Content-MD5");
    RESPONSE_HEADER("response.header.content-range","Content-Range");
    RESPONSE_HEADER("response.header.content-type","Content-Type");
    RESPONSE_HEADER("response.header.last-modified","Last-Modified");
    RESPONSE_HEADER("response.header.transfer-encoding","Transfer-Encoding");
    RESPONSE_HEADER("response.header.etag","ETag");
    RESPONSE_HEADER("response.header.via","Via");
    RESPONSE_HEADER("response.header.vary","Vary");
    RESPONSE_HEADER("response.header.pragma","Pragma");
    RESPONSE_HEADER("response.header.age","Age");
    RESPONSE_HEADER("response.header.accept-ranges","Accept-Ranges");
    RESPONSE_HEADER("response.header.set-cookie","Set-Cookie");
    RESPONSE_HEADER("response.header.via","Via");
    RESPONSE_HEADER("response.header.www-authenticate","WWW-Authenticate");

    elements["response.part"] = pelem(new keyword_params<handler_factory_t_arg<string, response_part> >());
    
    elements["response.header.value"] = pelem(new keyword_params<header_handler_factory_t<regex_handler_response> >());
    //elements["response.header.grep"] = pelem(new keyword_params_and_arg<regex_handler_factory_t<regex_handler_response> >());
    elements["response.header.grep"] = pelem(new keyword_params_and_arg<regex_handler_factory_t<regex_handler_response> >(_default_not_found));

    elements["idle.time.0"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, idle_time_1> >(_default_not_found));
    elements["idle.time.1"] = pelem(new keyword_optional_params<handler_factory_t_arg<string, idle_time_2> >(_default_not_found));

    elements["tab"] = pelem(new keyword_arg<string, handler_factory_t_arg<string, constant> >(string("\t")));
    elements["-"] = pelem(new break_keyword< handler_factory_t<basic_handler> >());
    elements["%"] = pelem(new keyword_arg<string, handler_factory_t_arg<string, constant> >(string("%")));
    elements["newline"] = pelem(new keyword_arg<string, handler_factory_t_arg<string, constant> >(string("\n")));
    _already_init = true;
}

void parser::process_open_connection(tcp_stream *ts, struct timeval* t, unsigned char* packet)
{
	connections[ts->addr]->onOpen( ts, t);
}

void parser::process_opening_connection(tcp_stream *ts, struct timeval* t, unsigned char* packet)
{
	streams::const_iterator it = connections.find(ts->addr);
	if (it == connections.end())
	{
		stream::ptr pstream(new stream(factories.begin(), factories.end(), _printer));
		pstream->onOpening( ts, t);
		connections[ts->addr]= pstream;
	}	
}

void parser::process_server(tcp_stream *ts, struct timeval* t, unsigned char* packet)
{
	connections[ts->addr]->onResponse(ts, t);
}

void parser::process_client(tcp_stream *ts, struct timeval* t, unsigned char* packet)
{
	connections[ts->addr]->onRequest(ts, t);
}

void parser::process_close_connection(tcp_stream *ts, struct timeval* t, unsigned char* packet)
{
	connections[ts->addr]->onClose(ts, t, packet);
	connections.erase(ts->addr);
	//cout << "connections.erase\n";
}

///// keyword_base /////
const char reserved_chars[] = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ._";

const char* keyword_common::parse(const char* cursor, const string& _keyword, handler_factories& factories)
{
	string keyword(_keyword);
	string::const_iterator start = keyword.begin();
	string::const_iterator end = keyword.end();
	if (equal(start, end, cursor+1))
	{
		const char* newpos = cursor+(end-start)+1;
		const char* end = reserved_chars+sizeof(reserved_chars);
		if ((*newpos == 0) ||(find(reserved_chars, end, *newpos) == end ))
		{
			push_back(factories);
			return newpos;
		}
	}
	return cursor;
}

///// keyword_params_base /////

const char keyword_params_base::start ='(';
const char keyword_params_base::end =')';

const char* keyword_params_base::parse_params(const char* cursor )
{
	const char* newcur = cursor;
	bool found=false;
	int in_par = 0;
	for (bool cont = true;cont;++newcur)
	{
		if (*newcur == start)
		{
			++in_par;
		}
		else if (*newcur == end)
		{
			if (!(--in_par))
			{
				cont = false;
				found = true;
			}
		}
		else
			switch (*newcur)
			{
				case 0:
					cont = false;
					break;
				default:
					if (!in_par)
						cont = false;
					break;
			}
	}
	if (found)
		return newcur;
	else
		return cursor;
}

const char* keyword_params_base::parse(const char* cursor, const string& _keyword, handler_factories& factories)
{
	const char* newcur = keyword_common::parse(cursor, _keyword, factories);
	if (newcur != cursor)
	{
		const char* params = parse_params(newcur);
		if (params != newcur)
		{
			factories.push_back(create_new_factory(string (newcur+1, params-1)));
			return params;
		}
	}
	return cursor;
	/*
	if (newcur != cursor)
	{
		string frm;
		bool found=false;
		int in_par = 0;
		for (bool cont = true;cont;++newcur)
		{
			if (*newcur == start)
			{
				if (in_par)
					frm += *newcur;
				++in_par;
			}
			else if (*newcur == end)
			{
				if (!(--in_par))
				{
					cont = false;
					found = true;
				}
				else
					frm += *newcur;
			}
			else
				switch (*newcur)
				{
					case 0:
						cont = false;
						break;
					default:
						if (in_par)
							frm += *newcur;
						else
							cont = false;
						break;
				}
		}
		if (found)
		{
			factories.push_back(create_new_factory(frm));
			return newcur;
		}
	}
	return cursor;	
	*/
}
///// keyword_optional_params_base ////

const char* keyword_optional_params_base::parse(const char* cursor, const string& _keyword, handler_factories& factories)
{
	const char* newcur = keyword_common::parse(cursor, _keyword, factories);
	if (newcur != cursor)
	{
		const char* params = parse_params(newcur);
		if (params != newcur)
		{
			factories.push_back(create_new_factory(string (newcur+1, params-1)));
			return params;
		}
		else
		{
			factories.push_back(create_new_factory(_default_arg));
			return newcur;
		}	
	}
	return cursor;
	
}

///// break_keyword_base ////

const char* break_keyword_base::parse(const char* cursor, const string& _keyword, handler_factories& factories)
{
	string keyword(_keyword);
	string::const_iterator start = keyword.begin();
	string::const_iterator end = keyword.end();
	if (equal(start, end, cursor+1))
	{
		//const char* newpos = cursor+(end-start)+1;
		push_back(factories);
		return cursor+(end-start)+1;
	}
	else
		return cursor;
}

///// outstream_printer/////


///// cmd_execute_printer //////
void cmd_execute_printer::_execute(handlers::iterator start, handlers::iterator end,const timeval*t)
{
	FILE *output  = NULL;
    output = popen (_command.c_str(), "w");
	try
	{
		check (output != NULL, cannot_execute_command(_command));
		{
		__gnu_cxx::stdio_filebuf<char> _ob(output, ios::out) ;
		std::ostream _out(&_ob) ;
		for (handlers::iterator i= start; i!= end; i++)
		{
			(*i)->append(_out, t);
		}
		_out.flush();
		}
	}
	catch(...)
	{	
		cerr << "Exception \n";
	}
	pclose(output);
}

void cmd_execute_printer::doit(handlers::iterator start, handlers::iterator end,const timeval*t)
{
	signal(SIGPIPE, SIG_IGN);
	if (!_user.empty())
	{
		run_as r (_user);
		_execute(start, end , t);
	}
	else
		_execute(start, end , t);
}

void outstream_printer::doit(handlers::iterator start, handlers::iterator end,const timeval*t)
{
	for (handlers::iterator i= start; i!= end; i++)
		(*i)->append(_out, t);
	_out<<std::endl<<std::flush;
	//_out.sync();
	fflush(stdout);
}

///// stream /////

int stream::id = 0;

stream::stream(handler_factories::iterator _begin, handler_factories::iterator _end, printer* printer):
		begin(_begin), end(_end), status(unknown), _printer(printer), tot_requests(0)
		{
		    id++;
		    _id=id;
		}


void stream::onOpening(tcp_stream* pstream, const timeval* t)
{
	//cout<<"stream::onOpen\n";
	init(pstream);
	opening_time = *t;
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->onOpening(this, t);
	status = opening;
}


void stream::onOpen(tcp_stream* pstream, const timeval* t)
{
	copy_tcp_stream(pstream);
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->onOpen(this, t);
	status = open;
}

void stream::onClose(tcp_stream* pstream, const timeval* t,unsigned char* packet)
{
	copy_tcp_stream(pstream);
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->onClose(this, t,packet);
	// don't print log for only open connection. (hmmmm, i should think more about it)
	if (status!=open)
	  print(t);
	//cout<<"stream::onClose end\n";
	tot_requests = 0;
	status=close;
}

void stream::onRequest(tcp_stream* pstream, const timeval* t)
{
	copy_tcp_stream(pstream);
	
	if (status == response)
	{
		print(t);
	}
    if (status != request)
	    tot_requests++;
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
	{
		(*i)->onRequest(this, t);
	}
	status=request;
}

void stream::onResponse(tcp_stream* pstream, const timeval* t)
{
	copy_tcp_stream(pstream);
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->onResponse(this, t);
	status=response;
}

void stream::copy_tcp_stream(tcp_stream* pstream)
{
    addr = pstream->addr;
    nids_state = pstream->nids_state;
    listeners = pstream->listeners;
    client = pstream->client;
    server = pstream->server;
    next_node = pstream->next_node;
    prev_node = pstream->prev_node;
    hash_index = pstream->hash_index;
    next_time = pstream->next_time;
    prev_time = pstream->prev_time;
    read = pstream->read;
    next_free = pstream->next_free;
    user = pstream->user;
}

void stream::init(tcp_stream* pstream)
{
	copy_tcp_stream(pstream);
	this->reinit();
}

void stream::reinit()
{
	_handlers.erase(_handlers.begin(), _handlers.end());
	for ( handler_factories::iterator i= begin; i!= end;i++)
		_handlers.push_back((*i)->create_handler());
}

void stream::print(const timeval* t)
{
	_printer->doit(_handlers.begin(), _handlers.end(), t);
/*	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->append(_out, t);
	_out<<std::endl;
	_out.flush();*/
	reinit();
}

/////////////////

void close_originator::append(std::basic_ostream<char>& out, const timeval* t)
{
	if (closed)
	{
	  if (ip_originator == sip)
		  out <<"client";
	  else if (ip_originator == dip)
		  out <<"server";
	  else 
		out <<_not_found;//<< ip_originator<< " " << dip<< " "<<sip;
	  
	}
	else
		out <<_not_found;
	
}

void close_originator::onClose(tcp_stream* pstream, const timeval* t, unsigned char* packet)
{
	closed = true;
	if (packet)
	{
		struct ip *this_iphdr = (struct ip *)packet;
		struct tcphdr *this_tcphdr = (struct tcphdr *)(packet + 4 * this_iphdr->ip_hl);
		ip_originator = this_iphdr->ip_src.s_addr;
	}
}

void close_originator::onOpen(tcp_stream* pstream, const timeval* t)
{
	sip = pstream->addr.saddr;
	dip = pstream->addr.daddr;
}

void close_originator::onOpening(tcp_stream* pstream, const timeval* t)
{
	sip = pstream->addr.saddr;
	dip = pstream->addr.daddr;
}

void close_originator::onRequest(tcp_stream* pstream, const timeval* t)
{
	sip = pstream->addr.saddr;
	dip = pstream->addr.daddr;
}
void close_originator::onResponse(tcp_stream* pstream,const  timeval* t)
{
	sip = pstream->addr.saddr;
	dip = pstream->addr.daddr;
}

