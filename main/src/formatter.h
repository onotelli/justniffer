/*
	Copyright (c) 2007 Plecno s.r.l. All Rights Reserved
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>
*/

#ifndef _sniffer_formatter_h
#define _sniffer_formatter_h
#include "config.h"
#include <vector>
#include <map>
#include <ostream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <sys/time.h>
#include <nids2.h>
#include <boost/shared_ptr.hpp>
#include <boost/iostreams/categories.hpp>
#include <boost/iostreams/operations.hpp>
#include <boost/iostreams/concepts.hpp>
#ifdef HAVE_BOOST_PYTHON
#include <boost/python.hpp>
#endif //HAVE_BOOST_PYTHON
#include "utilities.h"

#define DEFAULT_TIMEFORMAT "%Y-%m-%d %T"
static const std::string default_timeformat (DEFAULT_TIMEFORMAT);

class ascii_filter : public boost::iostreams::output_filter
{
public:
	typedef char char_type;
	typedef boost::iostreams::output_filter_tag category;

	template <typename Sink>
	bool put(Sink &snk, char c)
	{
		return boost::iostreams::put(snk, (std::isprint(c) || (c == '\n' || c == '\t')) ? c : '.');
	}
};

class ascii_filter_ext : public boost::iostreams::output_filter
{
public:
	typedef char char_type;
	typedef boost::iostreams::output_filter_tag category;

	template <typename Sink>
	bool put(Sink &snk, char c)
	{
		if (std::isprint(c) || (c == '\n' || c == '\t'))
			return boost::iostreams::put(snk, c);
		else
		{
			std::stringstream ss;
			ss << "[0x" << hex << (unsigned int)(unsigned char)c << "]";
			std::string str = ss.str();
			boost::iostreams::write(snk, str.c_str(), str.size());
			return true;
		}
	}
};

class connections_container
{
public:
	virtual int connection_number() = 0;
};

class handler : public shared_obj<handler>
{
public:
	virtual void onOpening(tcp_stream *pstream, const timeval *t) = 0;
	virtual void onOpen(tcp_stream *pstream, const timeval *t) = 0;
	virtual void onRequest(tcp_stream *pstream, const timeval *t) = 0;
	virtual void onResponse(tcp_stream *pstream, const timeval *t) = 0;
	virtual void append(std::basic_ostream<char> &out, const timeval *t, connections_container *pconnections_container) = 0;
	virtual void onClose(tcp_stream *pstream, const timeval *, unsigned char *packet) = 0;
	virtual void onTimedOut(tcp_stream *pstream, const timeval *, unsigned char *packet) = 0;
	virtual void onInterrupted() = 0;
	virtual ~handler() {}
};

class basic_handler : public handler
{
	virtual void append(std::basic_ostream<char> &out, const timeval *t, connections_container *pconnections_container) {}
	virtual void onOpening(tcp_stream *pstream, const timeval *t) {}
	virtual void onOpen(tcp_stream *pstream, const timeval *t) {}
	virtual void onRequest(tcp_stream *pstream, const timeval *t) {}
	virtual void onResponse(tcp_stream *pstream, const timeval *t) {}
	virtual void onClose(tcp_stream *pstream, const timeval *, unsigned char *packet) {}
	virtual void onTimedOut(tcp_stream *pstream, const timeval *, unsigned char *packet) {}
	virtual void onInterrupted() {}
};

typedef std::vector<handler::ptr> handlers;

class handler_factory : public shared_obj<handler_factory>
{
public:
	virtual handler::ptr create_handler() = 0;
	virtual ~handler_factory() {}
};

template <class handler_t>
class handler_factory_t : public handler_factory
{
public:
	virtual handler::ptr create_handler()
	{
		return handler::ptr(new handler_t());
	}
};

template <class arg_t, class handler_t>
class handler_factory_t_arg : public handler_factory
{
public:
	handler_factory_t_arg(arg_t arg) : _arg(arg) {}
	virtual handler::ptr create_handler()
	{
		return handler::ptr(new handler_t(_arg));
	}
	arg_t _arg;
};

template <class arg_t, class arg2_t, class handler_t>
class handler_factory_t_arg2 : public handler_factory
{
public:
	handler_factory_t_arg2(arg_t arg) : _arg(arg) {}
	handler_factory_t_arg2(arg_t arg, arg2_t arg2) : _arg(arg), _arg2(arg2) {}
	virtual handler::ptr create_handler()
	{
		return handler::ptr(new handler_t(_arg, _arg2));
	}
	arg_t _arg;
	arg2_t _arg2;
};

typedef std::vector<handler_factory::ptr> handler_factories;

class parse_element : public shared_obj<parse_element>
{
public:
	virtual const char *parse(const char *cursor, const string &_keyword, handler_factories &factories) = 0;
	virtual ~parse_element() {}
};

class keyword_common : public parse_element
{
protected:
	virtual const char *parse(const char *cursor, const string &_keyword, handler_factories &factories);
	virtual void push_back(handler_factories &factories) = 0;
	virtual ~keyword_common() {}
};

class keyword_base : public keyword_common
{
protected:
	virtual handler_factory::ptr create_new_factory() = 0;
	virtual void push_back(handler_factories &factories) { factories.push_back(create_new_factory()); }
};

class break_keyword_base : public keyword_base
{
protected:
	virtual const char *parse(const char *cursor, const string &_keyword, handler_factories &factories);
};

class keyword_params_base : public keyword_common
{
protected:
	virtual handler_factory::ptr create_new_factory(const string &params) = 0;
	virtual void push_back(handler_factories &factories) {}
	const char *parse_params(const char *cursor);
	virtual const char *parse(const char *cursor, const string &_keyword, handler_factories &factories);

private:
	static const char start, end;
};

template <class handler_factory_t>
class keyword : public keyword_base
{
public:
	virtual handler_factory::ptr create_new_factory()
	{
		return handler_factory::ptr(new handler_factory_t());
	}
};

template <class handler_factory_t>
class break_keyword : public break_keyword_base
{
public:
	virtual handler_factory::ptr create_new_factory()
	{
		return handler_factory::ptr(new handler_factory_t());
	}
};

template <class arg_t, class handler_factory_t>
class keyword_arg : public keyword_base
{
public:
	keyword_arg(arg_t arg) : _arg(arg) {}
	virtual handler_factory::ptr create_new_factory()
	{
		return handler_factory::ptr(new handler_factory_t(_arg));
	}

private:
	arg_t _arg;
};

template <class arg_t, class arg2_t, class handler_factory_t>
class keyword_arg2 : public keyword_base
{
public:
	keyword_arg2(arg_t arg, arg2_t arg2) : _arg(arg), _arg2(arg2) {}
	virtual handler_factory::ptr create_new_factory()
	{
		return handler_factory::ptr(new handler_factory_t(_arg, _arg2));
	}

private:
	arg_t _arg;
	arg2_t _arg2;
};

template <class handler_factory_t>
class keyword_params : public keyword_params_base
{
public:
	virtual handler_factory::ptr create_new_factory(const string &params)
	{
		return handler_factory::ptr(new handler_factory_t(params));
	}
};

template <class handler_factory_t>
class keyword_params_and_arg : public keyword_params_base
{
public:
	keyword_params_and_arg(const string &arg) : _arg(arg) {}
	virtual handler_factory::ptr create_new_factory(const string &params)
	{
		return handler_factory::ptr(new handler_factory_t(params, _arg));
	}

private:
	string _arg;
};

class keyword_optional_params_base : public keyword_params_base
{
public:
	keyword_optional_params_base(const std::string &default_arg) : _default_arg(default_arg) {}
	virtual const char *parse(const char *cursor, const string &_keyword, handler_factories &factories);

private:
	string _default_arg;
};

template <class handler_factory_t>
class keyword_optional_params : public keyword_optional_params_base
{
public:
	keyword_optional_params(const string &default_arg) : keyword_optional_params_base(default_arg) {}
	virtual handler_factory::ptr create_new_factory(const string &params)
	{
		return handler_factory::ptr(new handler_factory_t(params));
	}
};

template <class handler_factory_t>
class keyword_arg_and_optional_params : public keyword_optional_params<handler_factory_t>
{
public:
	keyword_arg_and_optional_params(const string &arg, const string &default_param) : keyword_optional_params<handler_factory_t>(arg), _arg(default_param) {}
	virtual handler_factory::ptr create_new_factory(const string &params)
	{
		return handler_factory::ptr(new handler_factory_t(params, _arg));
	}

private:
	string _arg;
};

template <class handler_factory_t>
class keyword_arg_and_optional_not_found : public keyword_optional_params<handler_factory_t>
{
public:
	keyword_arg_and_optional_not_found(const string &arg, const string &default_param) : keyword_optional_params<handler_factory_t>(default_param), _arg(arg) {}
	virtual handler_factory::ptr create_new_factory(const string &params)
	{
		return handler_factory::ptr(new handler_factory_t(_arg, params));
	}

private:
	string _arg;
};

class printer : public shared_obj<printer>
{
public:
	virtual void doit(handlers::iterator start, handlers::iterator end, const timeval *t, connections_container *pconnections_container) = 0;
	virtual ~printer() {};
};

class outstream_printer : public printer
{
public:
	typedef std::basic_ostream<char> &Out;
	// typedef T& Out;
	outstream_printer(Out out, bool skip_newline) : _out(out),_skip_newline(skip_newline) { _out.setf(ios_base::fixed); }
	void doit(handlers::iterator start, handlers::iterator end, const timeval *t, connections_container *pconnections_container);

private:
	bool _skip_newline;
	Out _out;
};

class cmd_execute_printer : public printer
{
public:
	typedef std::basic_ostream<char> &Out;
	cmd_execute_printer(std::string command) : _command(command) {}
	cmd_execute_printer(std::string command, std::string user) : _command(command), _user(user) {}
	void doit(handlers::iterator start, handlers::iterator end, const timeval *t, connections_container *pconnections_container);

private:
	void _execute(handlers::iterator start, handlers::iterator end, const timeval *t, connections_container *pconnections_container);
	std::string _command, _user;
};

#ifdef HAVE_BOOST_PYTHON
namespace py = boost::python;

class python_printer : public printer
{
public:
	python_printer(std::string script);
	python_printer(std::string script, std::string user);
	virtual void doit(handlers::iterator start, handlers::iterator end, const timeval *t, connections_container *pconnections_container);	
	virtual ~python_printer();
private:
	void _init();
	void _init_instance(std::string script_name, std::string func, py::object main_namespace);
	std::string _script;
	std::string _user;
	py::object instance;
	bool _finalized;
}; 
#endif //HAVE_BOOST_PYTHON

class stream : public shared_obj<stream>, public tcp_stream
{
	enum status_enum
	{
		unknown,
		opening,
		open,
		request,
		response,
		close,
		timedout,
		interrupted
	};

public:
	timeval opening_time;
	unsigned tot_requests;
	void copy_tcp_stream(tcp_stream *pstream);
	stream(handler_factories::iterator _begin, handler_factories::iterator _end, printer *printer, connections_container *pconnection_container);
	virtual void onOpening(tcp_stream *pstream, const timeval *t);
	virtual void onOpen(tcp_stream *pstream, const timeval *t);
	virtual void onClose(tcp_stream *pstream, const timeval *t, unsigned char *packet);
	virtual void onTimedOut(tcp_stream *pstream, const timeval *t, unsigned char *packet);
	virtual void onRequest(tcp_stream *pstream, const timeval *t);
	virtual void onResponse(tcp_stream *pstream, const timeval *t);
	virtual void onInterrupted();
	virtual ~stream() {};
	virtual void init(tcp_stream *pstream);
	virtual void reinit();
	virtual void print(const timeval *t);

protected:
	stream() {}

private:
	static int id;
	int _id;
	connections_container *_pconnection_container;
	handler_factories::iterator begin, end;
	handlers _handlers;
	status_enum status;
	printer *_printer;
};

typedef std::basic_ostream<char> &Out;
// typedef std::basic_ostream<char>* pOut;

class parser : public connections_container
{
public:
	typedef struct conn_info_
	{
		conn_info_(stream::ptr _stream_ptr, timeval _t) : stream_ptr(_stream_ptr), t(_t) {};
		conn_info_() {};
		stream::ptr stream_ptr;
		timeval t;
	} conn_info;

	typedef std::map<std::string, parse_element::ptr> parse_elements;
	typedef std::map<struct tuple4, conn_info> streams;
	typedef std::multimap<struct timeval, struct tuple4> streamtimes_index_type;

	parser()
	{
		init();
	}

	parser(printer *printer) : _printer(printer)
	{
		init();
	}
	parse_elements::iterator keywords_begin()
	{
		init_parse_elements();
		return elements.begin();
	}
	parse_elements::iterator keywords_end()
	{
		init_parse_elements();
		return elements.end();
	}
	static void nids_handler(struct tcp_stream *ts, void **yoda, struct timeval *t, unsigned char *packet);
	void parse(const char *format);
	virtual ~parser() { theOnlyParser = NULL; };
	void set_printer(printer *printer) { _printer = printer; }
	void set_handle_truncated(bool value) { handle_truncated = value; }
	void set_default_not_found(const std::string &default_not_found) { _default_not_found = default_not_found; }
	void set_user(const std::string& user){_user = user;}
	bool _already_init;
	virtual int connection_number();
	void process_truncated();

private:
	bool handle_truncated;
	void init()
	{
		_already_init = false;
		check(theOnlyParser == NULL, common_exception("parser::parser(): I am not the only parser"));
		theOnlyParser = this;
	}

	const char *_parse_element(const char *format);
	void init_parse_elements();
	void process_opening_connection(tcp_stream *ts, struct timeval *t, unsigned char *packet);
	void process_open_connection(tcp_stream *ts, struct timeval *t, unsigned char *packet);
	void process_server(tcp_stream *ts, struct timeval *t, unsigned char *packet);
	stream::ptr get_stream(const tuple4 &t);
	void process_client(tcp_stream *ts, struct timeval *t, unsigned char *packet);
	void process_close_connection(tcp_stream *ts, struct timeval *t, unsigned char *packet);
	void process_timedout_connection(tcp_stream *ts, struct timeval *t, unsigned char *packet);

	parse_elements elements;
	streams connections;
	// streamtimes_index_type streamtimes_index;

	handler_factories factories;
	printer *_printer;
	std::string _default_not_found;
	std::string _user;

public:
	static parser *theOnlyParser;
	static const char _key_word_id;
};

class unknown_keyword : public common_exception
{
public:
	unknown_keyword(const string &str) : common_exception(string("unknown keyword '").append(str).append("'")) {}
};

class parser_not_initialized : public common_exception
{
public:
	parser_not_initialized() : common_exception("parser non initializated") {}
};

class cannot_execute_command : public common_exception
{
public:
	cannot_execute_command(const string &command) : common_exception(string("cannot execute command: ").append(command)) {}
};

///// handlers /////
template <class base>
class request_header_collector : public base
{
public:
	request_header_collector() : complete(false) {}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		if (!complete)
			complete = get_headers(pstream->server.data, pstream->server.data + pstream->server.count_new, text);
	}

private:
	bool complete;

protected:
	string text;
};

template <class base>
class request_body_collector : public base
{
public:
	request_body_collector() :header_complete(false){}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		header_complete = get_body(pstream->server.data, pstream->server.data + pstream->server.count_new, text, header_complete);
	}

protected:
	string text;
private:
	bool header_complete;

};



template <class base>
class response_header_collector : public base
{
public:
	response_header_collector() : complete(false) {}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		if (!complete)
			complete = get_headers(pstream->client.data, pstream->client.data + pstream->client.count_new, text);
	}

private:
	bool complete;

protected:
	string text;
};

template <class base>
class response_body_collector : public base
{
public:
	response_body_collector():header_complete(false) {}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		header_complete = get_body(pstream->client.data, pstream->client.data + pstream->client.count_new, text, header_complete);
	}

protected:
	string text;
private:
	bool header_complete;
};


template <class base>
class request_collector : public base
{
public:
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		text += string(pstream->server.data, pstream->server.data + pstream->server.count_new);
	}

protected:
	string text;
};

template <class base>
class response_collector : public base
{
public:
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		text += string(pstream->client.data, pstream->client.data + pstream->client.count_new);
	}

protected:
	string text;
};

class string_handler : public basic_handler
{
public:
	string_handler(const string &str) : _str(str) {};
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << _str; };

private:
	std::string _str;
};

class string_handler_factory : public handler_factory
{
public:
	string_handler_factory(const string &str) : _str(str) {}
	virtual handler::ptr create_handler()
	{
		return handler::ptr(new string_handler(_str));
	}

private:
	std::string _str;
};

class connection_handler : public basic_handler
{

public:
	enum status
	{
		unknown,
		start,
		cont,
		last,
		uniq
	} stat;
	connection_handler() : stat(unknown) {};
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		switch (stat)
		{
		case start:
			out << "start";
			break;
		case cont:
			out << "continue";
			break;
		case last:
			out << "last";
			break;
		case uniq:
			out << "unique";
			break;
		default:
			out << "unknown";
			break;
		}
	}

	virtual void onOpening(tcp_stream *pstream, const timeval *t) { stat = start; }
	virtual void onOpen(tcp_stream *pstream, const timeval *t) { stat = start; }
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		if (stat == unknown)
			stat = cont;
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		if (stat == unknown)
			stat = cont;
	}
	virtual void onClose(tcp_stream *pstream, const timeval *, unsigned char *packet)
	{
		if (stat == start)
			stat = uniq;
		else
			stat = last;
	}
};

class ip_base : public basic_handler
{
public:
	ip_base() : ip(0) {}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << ip_to_str(ip); };

protected:
	u_long ip;
};

class port_base : public basic_handler
{
public:
	port_base() : port(0) {}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << int(port); };

protected:
	u_short port;
};

class source_ip : public ip_base
{
public:
	source_ip() {}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		ip = pstream->addr.saddr;
	}
	virtual void onOpening(tcp_stream *pstream, const timeval *t)
	{
		ip = pstream->addr.saddr;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t)
	{
		ip = pstream->addr.saddr;
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		ip = pstream->addr.saddr;
	}
	virtual void onClose(tcp_stream *pstream, const timeval *, unsigned char *packet)
	{
		ip = pstream->addr.saddr;
	}
};

class dest_ip : public ip_base
{
public:
	dest_ip() {}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		ip = pstream->addr.daddr;
	}
	virtual void onOpening(tcp_stream *pstream, const timeval *t)
	{
		ip = pstream->addr.daddr;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t)
	{
		ip = pstream->addr.daddr;
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		ip = pstream->addr.daddr;
	}
	virtual void onClose(tcp_stream *pstream, const timeval *, unsigned char *packet)
	{
		ip = pstream->addr.daddr;
	}
};

class source_port : public port_base
{
public:
	source_port() {}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		port = pstream->addr.source;
	}
	virtual void onOpening(tcp_stream *pstream, const timeval *t)
	{
		port = pstream->addr.source;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t)
	{
		port = pstream->addr.source;
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		port = pstream->addr.source;
	}
	virtual void onClose(tcp_stream *pstream, const timeval *, unsigned char *packet)
	{
		port = pstream->addr.source;
	}
};

class dest_port : public port_base
{
public:
	dest_port() {}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		port = pstream->addr.dest;
	}
	virtual void onOpening(tcp_stream *pstream, const timeval *t)
	{
		port = pstream->addr.dest;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t)
	{
		port = pstream->addr.dest;
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		port = pstream->addr.dest;
	}
	virtual void onClose(tcp_stream *pstream, const timeval *, unsigned char *packet)
	{
		port = pstream->addr.dest;
	}
};

class constant : public basic_handler
{
public:
	constant(const string &constant) : _constant(constant) {}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << _constant; };

protected:
	string _constant;
};

class current_streams : public basic_handler
{
public:
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << pconnections_container->connection_number(); };
};

template <class base>
class collect_first_line_request : public base
{
public:
	collect_first_line_request() : complete(false) {}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		if (!complete)
			complete = get_first_line(pstream->server.data, pstream->server.data + pstream->server.count_new, text);
	}

private:
	bool complete;

protected:
	string text;
};

template <class base>
class collect_first_line_response : public base
{
public:
	collect_first_line_response() : complete(false) {}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		if (!complete)
			complete = get_first_line(pstream->client.data, pstream->client.data + pstream->client.count_new, text);
	}

private:
	bool complete;

protected:
	string text;
};

class request_first_line : public collect_first_line_request<basic_handler>
{
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << text; }
};

class response_first_line : public collect_first_line_response<basic_handler>
{
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << text; }
};

class timestamp_handler_base : public basic_handler
{
protected:
	typedef std::basic_ostream<char> &out_type;
	timestamp_handler_base(const string &not_found) : _not_found(not_found)
	{
		time.tv_sec = 0;
		time.tv_usec = 0;
	}
	timestamp_handler_base()
	{
		time.tv_sec = 0;
		time.tv_usec = 0;
	}

public:
	virtual void append(out_type out, const timeval *, connections_container *pconnections_container)
	{
		if ((time.tv_sec == 0) && (time.tv_usec == 0))
			out << _not_found;
		else
			print_out_time_stamp(out);
	};

protected:
	virtual void print_out_time_stamp(out_type out) = 0;
	string _not_found;
	timeval time;
};

class timestamp_handler : public timestamp_handler_base
{
public:
	timestamp_handler(): is_default_format(false){}
	timestamp_handler(const string &format) : fmt(format),  is_default_format(format.compare(default_timeformat)== 0) {}
	timestamp_handler(const string &format, const string &not_found) : timestamp_handler_base(not_found), fmt(format), is_default_format(format.compare( default_timeformat) ==0) {}

protected:
	virtual void print_out_time_stamp(out_type out)
	{
		out <<timestamp(&time, fmt);
		if (fmt == default_timeformat)
			out << "." << std::left << std::setfill('0') << std::setw(6) << time.tv_usec;
	}
	string fmt;

private:
	bool is_default_format;
	
};

class timestamp_handler2 : public timestamp_handler_base
{
public:
	timestamp_handler2() {}
	timestamp_handler2(const string &not_found) : timestamp_handler_base(not_found) {}

protected:
	virtual void print_out_time_stamp(out_type out)
	{
		out << time.tv_sec << "." << time.tv_usec;
	}
};

template <class base>
class request_timestamp_handler_base : public base
{
public:
	request_timestamp_handler_base(): base(){}
	request_timestamp_handler_base(const string &format) : base(format) {}
	request_timestamp_handler_base(const string &format, const string &not_found) : base(format, not_found) {}	
	virtual void onRequest(tcp_stream *pstream, const timeval *t) { this->time = *t; }
};

template <class base>
class connection_timestamp_handler_base : public base
{
public:
	connection_timestamp_handler_base(): base(){}
	connection_timestamp_handler_base(const string &format) : base(format) {}
	connection_timestamp_handler_base(const string &format, const string &not_found) : base(format, not_found) {}	
	virtual void onOpening(tcp_stream *pstream, const timeval *t) { this->time = *t; }
};

template <class base>
class response_timestamp_handler_base : public base
{
public:
	response_timestamp_handler_base(): base(){}
	response_timestamp_handler_base(const string &format) : base(format) {}
	response_timestamp_handler_base(const string &format, const string &not_found) : base(format, not_found) {}	
	virtual void onResponse(tcp_stream *pstream, const timeval *t) { this->time = *t; }
};

template <class base>
class close_timestamp_handler_base : public base
{
public:
	close_timestamp_handler_base(): base(){}
	close_timestamp_handler_base(const string &format) : base(format) {}
	close_timestamp_handler_base(const string &format, const string &not_found) : base(format, not_found) {}	
	virtual void onClose(tcp_stream *pstream, const timeval *t, unsigned char *packet) { this->time = *t; }
};

class request_timestamp_handler : public request_timestamp_handler_base<timestamp_handler>
{
public:
	request_timestamp_handler(): request_timestamp_handler_base(){}
	request_timestamp_handler(const string &format) : request_timestamp_handler_base(format) {}
	request_timestamp_handler(const string &format, const string &not_found) : request_timestamp_handler_base(format, not_found) {}	
};

class connection_timestamp_handler : public connection_timestamp_handler_base<timestamp_handler>
{
public:
	connection_timestamp_handler(): connection_timestamp_handler_base(){}
	connection_timestamp_handler(const string &format) : connection_timestamp_handler_base(format) {}
	connection_timestamp_handler(const string &format, const string &not_found) : connection_timestamp_handler_base(format, not_found) {}	
};

class response_timestamp_handler : public response_timestamp_handler_base<timestamp_handler>
{
public:
	response_timestamp_handler(): response_timestamp_handler_base(){}
	response_timestamp_handler(const string &format) : response_timestamp_handler_base(format) {}
	response_timestamp_handler(const string &format, const string &not_found) : response_timestamp_handler_base(format, not_found) {}	
};

class close_timestamp_handler : public close_timestamp_handler_base<timestamp_handler>
{
public:
	close_timestamp_handler(): close_timestamp_handler_base(){}
	close_timestamp_handler(const string &format) : close_timestamp_handler_base(format) {}
	close_timestamp_handler(const string &format, const string &not_found) : close_timestamp_handler_base(format, not_found) {}	
};

class request_timestamp_handler2 : public request_timestamp_handler_base<timestamp_handler2>
{
public:
	request_timestamp_handler2(const string &not_found) { _not_found = not_found; }
};

class connection_timestamp_handler2 : public connection_timestamp_handler_base<timestamp_handler2>
{
public:
	connection_timestamp_handler2(const string &not_found) { _not_found = not_found; }
};

class response_timestamp_handler2 : public response_timestamp_handler_base<timestamp_handler2>
{
public:
	response_timestamp_handler2(const string &not_found) { _not_found = not_found; }
};

class close_timestamp_handler2 : public close_timestamp_handler_base<timestamp_handler2>
{
public:
	close_timestamp_handler2(const string &not_found) { _not_found = not_found; }
};

class response_time_handler : public basic_handler
{
public:
	response_time_handler(const string &not_found)
	{
		response = false;
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (response)
			out << to_double(t2 - t1);
		else
			out << _not_found;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t) { t1 = *t; }
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		response = true;
		t2 = *t;
	}
	virtual void onRequest(tcp_stream *pstream, const timeval *t) { t1 = *t; }
	virtual void onClose(tcp_stream *pstream, const timeval *t, unsigned char *packet)
	{
		if (!response)
			t2 = *t;
	}

private:
	bool response;
	timeval t1, t2;
	string _not_found;
};

class request_time_handler : public basic_handler
{
public:
	request_time_handler(const string &not_found)
	{
		requested_started = false;
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (requested_started)
			out << to_double(t2 - t1);
		else
			out << _not_found;
	}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		if (!requested_started)
			t1 = *t;
		t2 = *t;
		requested_started = true;
	}

private:
	bool requested_started;
	timeval t1, t2;
	string _not_found;
};

class idle_time_2 : public basic_handler
{
public:
	idle_time_2(const string &not_found)
	{
		response = false;
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *t, connections_container *pconnections_container)
	{
		if (t && response) {
			t2 = *t;
			out << to_double(t2 - t1);
		} else {
			out << _not_found;
		}	
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		t1 = *t;
		response = true;
	}

private:
	timeval t1, t2;
	bool response;
	string _not_found;
};

class idle_time_1 : public basic_handler
{
public:
	idle_time_1(const string &not_found)
	{
		open = false;
		request = false;
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t)
	{
		t1 = *t;
		open = true;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (open && request)
			out << to_double(t2 - t1);
		else
			out << _not_found;
	}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		if (!request)
			t2 = *t;
		request = true;
	}

private:
	timeval t1, t2;
	bool request, open;
	string _not_found;
};

class response_time_1 : public basic_handler
{
public:
	response_time_1(const string &not_found)
	{
		response = false;
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (response)
			out << to_double(t2 - t1);
		else
			out << _not_found;
	}
	virtual void onRequest(tcp_stream *pstream, const timeval *t) { t1 = *t; }
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		if (!response)
			t2 = *t;
		response = true;
	}

private:
	timeval t1, t2;
	bool response;
	string _not_found;
};

class response_time_2 : public basic_handler
{
public:
	response_time_2(const string &not_found)
	{
		response = false;
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (response)
			out << to_double(t2 - t1);
		else
			out << _not_found;
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		if (!response)
			t1 = *t;
		t2 = *t;
		response = true;
	}

private:
	bool response;
	timeval t1, t2;
	string _not_found;
};

class close_time : public basic_handler
{
public:
	close_time(const string &not_found)
	{
		response = false;
		closed = false;
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (response && closed)
			out << to_double(t2 - t1);
		else
			out << _not_found;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t)
	{
		response = true;
		t1 = *t;
	}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		response = true;
		t1 = *t;
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		response = true;
		t1 = *t;
	}
	virtual void onClose(tcp_stream *pstream, const timeval *t, unsigned char *packet)
	{
		t2 = *t;
		closed = true;
	}

private:
	bool closed, response;
	timeval t1, t2;
	string _not_found;
};

class close_originator : public basic_handler
{
public:
	close_originator(const string &not_found)
	{
		stat = unknown, ip_originator = 0, sip = 0, dip = 0, dport =0, sport = 0;
		
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container);
	virtual void onOpening(tcp_stream *pstream, const timeval *t);
	virtual void onOpen(tcp_stream *pstream, const timeval *t);
	virtual void onClose(tcp_stream *pstream, const timeval *t, unsigned char *packet);
	virtual void onTimedOut(tcp_stream *pstream, const timeval *t, unsigned char *packet);
	virtual void onRequest(tcp_stream *pstream, const timeval *t);
	virtual void onResponse(tcp_stream *pstream, const timeval *t);
	virtual void onInterrupted();

private:
	enum status
	{
		unknown,
		closed,
		timedout,
		truncated
	};
	status stat;
	u_int32_t ip_originator, sip, dip;
	uint16_t port_originator, sport, dport;
	string _not_found;
};

class connection_time_handler : public basic_handler
{
public:
	connection_time_handler(const string &not_found)
	{
		connection_started = false;
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (t1.tv_sec & t2.tv_sec)
			out << to_double(t2 - t1);
		else
			out << _not_found;
	}
	virtual void onOpening(tcp_stream *pstream, const timeval *t)
	{
		if (!connection_started)
			t1 = *t;
		;
		connection_started = true;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t) { t2 = *t; }

private:
	bool connection_started;
	timeval t1, t2;
	string _not_found;
};

class session_time_handler : public basic_handler
{
public:
	session_time_handler(const string &not_found)
	{
		t1.tv_sec = 0;
		t1.tv_usec = 0;
		t2.tv_sec = 0;
		t2.tv_usec = 0;
		_not_found = not_found;
	}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (t1.tv_sec & t2.tv_sec)
			out << to_double(t2 - t1);
		else
			out << _not_found;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t)
	{
		t1 = ((stream *)pstream)->opening_time;
		t2 = *t;
	}
	virtual void onRequest(tcp_stream *pstream, const timeval *t)
	{
		t1 = ((stream *)pstream)->opening_time;
		t2 = *t;
	}
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		t1 = ((stream *)pstream)->opening_time;
		t2 = *t;
	}
	virtual void onOpening(tcp_stream *pstream, const timeval *t)
	{
		t1 = ((stream *)pstream)->opening_time;
		t2 = ((stream *)pstream)->opening_time;
	}
	virtual void onClose(tcp_stream *pstream, const timeval *t, unsigned char *packet)
	{
		t1 = ((stream *)pstream)->opening_time;
		t2 = *t;
	}

private:
	timeval t1, t2;
	string _not_found;
};

class session_request_counter : public basic_handler
{
public:
	session_request_counter(const string &not_found) : _pstream(0), _not_found(not_found) {}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container)
	{
		if (!_pstream)
			out << _not_found;
		else
			out << _pstream->tot_requests;
	}
	virtual void onOpen(tcp_stream *pstream, const timeval *t) { _pstream = ((stream *)pstream); }
	virtual void onRequest(tcp_stream *pstream, const timeval *t) { _pstream = ((stream *)pstream); }
	virtual void onResponse(tcp_stream *pstream, const timeval *t) { _pstream = ((stream *)pstream); }
	virtual void onOpening(tcp_stream *pstream, const timeval *t) { _pstream = ((stream *)pstream); }
	virtual void onClose(tcp_stream *pstream, const timeval *t, unsigned char *packet) { _pstream = ((stream *)pstream); }

private:
	stream *_pstream;
	string _not_found;
};

class response_size_handler : public basic_handler
{
public:
	response_size_handler() : size(0) {}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << size; }
	virtual void onResponse(tcp_stream *pstream, const timeval *t)
	{
		size += pstream->client.count_new;
	}

private:
	int size;
};

class request_size_handler : public basic_handler
{
public:
	request_size_handler() : size(0) {}
	virtual void append(std::basic_ostream<char> &out, const timeval *, connections_container *pconnections_container) { out << size; }
	virtual void onRequest(tcp_stream *pstream, const timeval *t) { size += pstream->server.count_new; }

private:
	int size;
};


#ifdef HAVE_BOOST_PYTHON

class python_handler_factory :public handler_factory
{
public:
	python_handler_factory(const std::string& user ,const std::string& arg);
	virtual handler::ptr create_handler();
	virtual ~python_handler_factory();
private:	
	void _init (const std::string &arg); 
	std::string _arg;
	std::string _user;
	py::object _pyclass;
};



class python_handler: public handler{
public:
	python_handler(py::object &pyClass);
	virtual void append(std::basic_ostream<char> &out, const timeval *t, connections_container *pconnections_container);
    virtual void onOpening(tcp_stream *pstream, const timeval *t);
    virtual void onOpen(tcp_stream *pstream, const timeval *t);
	virtual void onRequest(tcp_stream *pstream, const timeval *t);
	virtual void onResponse(tcp_stream *pstream, const timeval *t);
	virtual void onClose(tcp_stream *pstream, const timeval *, unsigned char *packet);
	virtual void onTimedOut(tcp_stream *pstream, const timeval *, unsigned char *packet);
	virtual void onInterrupted();
private:
	py::object	_instance;
    void _handle_exception(const py::error_already_set &e);
	template <typename... Args> void call_python_method(const char* method_name, Args&&... args);


};
#endif //HAVE_BOOST_PYTHON


#endif // _sniffer_formatter_h
