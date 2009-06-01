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
	//cout << "nids_handler "<< (int)ts->nids_state << "\n";
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

void parser::init_parse_elements()
{
	elements["dest.ip"] = parse_element::ptr(new keyword<handler_factory_t<dest_ip> >());
	elements["source.ip"] = parse_element::ptr(new keyword<handler_factory_t<source_ip> >());
	elements["dest.port"] = parse_element::ptr(new keyword<handler_factory_t<dest_port> >());
	elements["source.port"] = parse_element::ptr(new keyword<handler_factory_t<source_port> >());

	elements["connection"] = parse_element::ptr(new keyword<handler_factory_t<connection_handler> >());
	elements["connection.time"] = parse_element::ptr(new keyword<handler_factory_t<connection_time_handler> >());
	elements["connection.timestamp"] = parse_element::ptr(new keyword_optional_params<handler_factory_t_arg<string, connection_timestamp_handler> > ("%D %T"));
	elements["close.time"] = parse_element::ptr(new keyword<handler_factory_t<close_time> >());
	elements["close.originator"] = parse_element::ptr(new keyword<handler_factory_t<close_originator> >());
	elements["request"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_all_request> >(string(".*")));
	elements["request.timestamp"] = parse_element::ptr(new keyword_optional_params<handler_factory_t_arg<string, request_timestamp_handler> > ("%D %T"));
	elements["request.time"] = parse_element::ptr(new keyword<handler_factory_t<request_time_handler> >());
	elements["request.size"] = parse_element::ptr(new keyword<handler_factory_t<request_size_handler> > ());
	elements["request.line"] = parse_element::ptr(new keyword<handler_factory_t<request_first_line> >());
	elements["request.method"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_request_line> >(string("(^[^\\s]*)")));
	elements["request.url"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_request_line> >(string("^[^\\s]*\\s*([^\\s]*)")));
	elements["request.protocol"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_request_line> >(string("^[^\\s]*\\s*[^\\s]*\\s*([^\\s]*)")));
	elements["request.grep"] = parse_element::ptr(new keyword_params<regex_handler_factory_t<regex_handler_all_request> >());
	elements["request.header"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_request> >(string(".*")));
	elements["request.header.host"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Host")));
	elements["request.header.user-agent"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("User-Agent")));
	elements["request.header.accept"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Accept")));
	elements["request.header.accept-charset"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Accept-Charset")));
	elements["request.header.accept-encoding"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Accept-Encoding")));
	elements["request.header.accept-language"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Accept-Language")));
	elements["request.header.authorization"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Authorization")));
	elements["request.header.keep-alive"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Keep-Alive")));
	elements["request.header.referer"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Referer")));
	elements["request.header.range"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Range")));
	elements["request.header.cookie"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Cookie")));
	elements["request.header.connection"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Connection")));
	elements["request.header.content-encoding"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Content-Encoding")));
	elements["request.header.content-language"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Content-Language")));
	elements["request.header.transfer-encoding"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Transfer-Encoding")));
	elements["request.header.content-length"] = parse_element::ptr(new keyword_arg2<string, string, regex_handler_factory_t_arg<regex_handler_request> >(string("^Content-Length:\\s*([^\\r]*)"), string("0")));
	elements["request.header.content-md5"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Content-MD5")));
	elements["request.header.via"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_request> >(string("Via")));
	elements["request.header.value"] = parse_element::ptr(new keyword_params<header_handler_factory_t<regex_handler_request> >());
	elements["request.header.grep"] = parse_element::ptr(new keyword_params<regex_handler_factory_t<regex_handler_request> >());

	elements["response"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_all_response> >(string(".*")));
	elements["response.timestamp"] = parse_element::ptr(new keyword_optional_params<handler_factory_t_arg<string, response_timestamp_handler> > ("%D %T"));
	elements["response.size"] = parse_element::ptr(new keyword<handler_factory_t<response_size_handler> > ());
	elements["response.time"] = parse_element::ptr(new keyword<handler_factory_t<response_time_handler> >());
	elements["response.time.begin"] = parse_element::ptr(new keyword<handler_factory_t<response_time_1> >());
	elements["response.time.end"] = parse_element::ptr(new keyword<handler_factory_t<response_time_2> >());
	elements["response.line"] = parse_element::ptr(new keyword<handler_factory_t<response_first_line> >());
	elements["response.protocol"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_response_line> >(string("(^[^\\s]*)")));
	elements["response.code"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_response_line> >(string("^[^\\s]*\\s*([^\\s]*)")));
	elements["response.message"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_response_line> >(string("^[^\\s]*\\s*[^\\s]*\\s*([^\\r]*)")));	
	elements["response.grep"] = parse_element::ptr(new keyword_params<regex_handler_factory_t<regex_handler_all_response> >());
	elements["response.header"] = parse_element::ptr(new keyword_arg<string, regex_handler_factory_t<regex_handler_response> >(string(".*")));
	elements["response.header.allow"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Allow")));
	elements["response.header.server"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Server")));
	elements["response.header.date"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Date")));
	elements["response.header.cache-control"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Cache-Control")));
	elements["response.header.keep-alive"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Keep-Alive")));
	elements["response.header.connection"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Connection")));
	elements["response.header.expires"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Expires")));
	elements["response.header.content-encoding"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Content-Encoding")));
	elements["response.header.content-language"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Content-Laguage")));
	elements["response.header.content-length"] = parse_element::ptr(new keyword_arg2<string, string, regex_handler_factory_t_arg<regex_handler_response> >(string("^Content-Length:\\s*([^\\r]*)"), string("0")));
	elements["response.header.content-md5"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Content-MD5")));
	elements["response.header.content-range"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Content-Range")));
	elements["response.header.content-type"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Content-Type")));
	elements["response.header.last-modified"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Last-Modified")));
	elements["response.header.transfer-encoding"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Transfer-Encoding")));
	elements["response.header.etag"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("ETag")));
	elements["response.header.via"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Via")));
	elements["response.header.vary"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Vary")));
	elements["response.header.pragma"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Pragma")));
	elements["response.header.age"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Age")));
	elements["response.header.accept-ranges"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Accept-Ranges")));
	elements["response.header.set-cookie"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Set-Cookie")));
	elements["response.header.via"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("Via")));
	elements["response.header.www-authenticate"] = parse_element::ptr(new keyword_arg<string, header_handler_factory_t<regex_handler_response> >(string("WWW-Authenticate")));
	
	elements["response.header.value"] = parse_element::ptr(new keyword_params<header_handler_factory_t<regex_handler_response> >());
	elements["response.header.grep"] = parse_element::ptr(new keyword_params<regex_handler_factory_t<regex_handler_response> >());

	elements["idle.time.0"] = parse_element::ptr(new keyword<handler_factory_t<idle_time_1> >());
	elements["idle.time.1"] = parse_element::ptr(new keyword<handler_factory_t<idle_time_2> >());
	//elements["session.time"] = parse_element::ptr(new keyword<handler_factory_t<session_time_handler> >());

	elements["tab"] = parse_element::ptr(new keyword_arg<string, handler_factory_t_arg<string, constant> >(string("\t")));
	elements["-"] = parse_element::ptr(new break_keyword< handler_factory_t<basic_handler> >());
	elements["%"] = parse_element::ptr(new keyword_arg<string, handler_factory_t_arg<string, constant> >(string("%")));
	elements["newline"] = parse_element::ptr(new keyword_arg<string, handler_factory_t_arg<string, constant> >(string("\n")));
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

void outstream_printer::doit(handlers::iterator start, handlers::iterator end,const timeval*t)
{
	for (handlers::iterator i= start; i!= end; i++)
		(*i)->append(_out, t);
	_out<<std::endl;
	_out.flush();
}

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

///// stream /////

void stream::onOpening(tcp_stream* pstream, const timeval* t)
{
	//cout<<"stream::onOpen\n";
	init();
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->onOpening(pstream, t);
	status = opening;
}


void stream::onOpen(tcp_stream* pstream, const timeval* t)
{
	//cout<<"stream::onOpen\n";
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->onOpen(pstream, t);
	status = open;
}

void stream::onClose(tcp_stream* pstream, const timeval* t,unsigned char* packet)
{
	//cout<<"stream::onClose\n";
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->onClose(pstream, t,packet);
	// don't print log for only open connection. (hmmmm, i should think more about it)
	if (status!=open)
	  print(t);
	//cout<<"stream::onClose end\n";
	status=close;
}

void stream::onRequest(tcp_stream* pstream, const timeval* t)
{
	if (status == response)
	{
		print(t);
	}
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
	{
		(*i)->onRequest(pstream, t);
	}
	status=request;
}

void stream::onResponse(tcp_stream* pstream, const timeval* t)
{
	//cout<<"stream::onResponse\n";
	for (handlers::iterator i= _handlers.begin(); i!= _handlers.end(); i++)
		(*i)->onResponse(pstream, t);
	status=response;
}

void stream::init()
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
	init();
}

/////////////////

void close_originator::append(std::basic_ostream<char>& out, const timeval* t)
{
	if (closed)
	if (ip_originator == sip)
		out <<"client";
	if (ip_originator == dip)
		out <<"server";
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

void close_originator::onRequest(tcp_stream* pstream, const timeval* t)
{
	sip = pstream->addr.saddr;
}
void close_originator::onResponse(tcp_stream* pstream,const  timeval* t)
{
	dip = pstream->addr.daddr;
}

