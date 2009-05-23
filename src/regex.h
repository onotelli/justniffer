/*
	Copyright (c) 2007 Plecno s.r.l. All Rights Reserved 
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>	
*/

#include <boost/regex.hpp>
#include <string>
#include <formatter.h>

std::string regex(const boost::regex& re, const std::string& text);

template <class handler_t>
class regex_handler_factory_t :public handler_factory
{
public:
	regex_handler_factory_t(const std::string& arg):_re(arg){}
	virtual handler::ptr create_handler()
	{
		return handler::ptr(new handler_t(_re));
	}
	boost::regex _re;
};

template <class handler_t>
class regex_handler_factory_t_arg :public handler_factory
{
public:
	regex_handler_factory_t_arg(const std::string& expr,const std::string& not_found):_re(expr), _not_found(not_found){}
	virtual handler::ptr create_handler()
	{
		return handler::ptr(new handler_t(_re, _not_found));
	}
	boost::regex _re;
	std::string _not_found;
};

class regex_handler_base: public basic_handler
{
public:
	virtual void append(std::basic_ostream<char>& out, const timeval* );

protected:
	virtual string& get_text() = 0;
	 boost::regex _re;
	 string _not_found;
};

class regex_handler_request: public request_header_collector<regex_handler_base>
{
public:
	regex_handler_request(const boost::regex& re, const std::string& not_found){_re=re; _not_found= not_found;}
	regex_handler_request(const boost::regex& re){_re=re;}
protected:
	virtual string& get_text() {return text;};

};

class regex_handler_response: public response_header_collector<regex_handler_base>
{
public:
	regex_handler_response(const boost::regex& re, const std::string& not_found){_re=re; _not_found= not_found;}
	regex_handler_response(const boost::regex& re){_re=re;}
protected:
	virtual string& get_text() {return text;};
};

class regex_handler_all_request: public request_collector<regex_handler_base>
{
public:
	regex_handler_all_request(const boost::regex& re){_re=re;}
protected:
	virtual string& get_text() {return text;};

};

class regex_handler_all_response: public response_collector<regex_handler_base>
{
public:
	regex_handler_all_response(const boost::regex& re){_re=re;}
protected:
	virtual string& get_text() {return text;};
};

template <class handler_t>
class header_handler_factory_t :public regex_handler_factory_t<handler_t>
{
public:
	header_handler_factory_t(const std::string& arg):regex_handler_factory_t<handler_t>(string(arg).append(":\\s*([^\\r]*)")){}
};

class regex_handler_request_line: public collect_first_line_request<regex_handler_base>
{
public:
	regex_handler_request_line(const boost::regex& re){_re=re;}
protected:
	virtual string& get_text() {return text;};
};

class regex_handler_response_line: public collect_first_line_response<regex_handler_base>
{
public:
	regex_handler_response_line(const boost::regex& re){_re=re;}
protected:
	virtual string& get_text() {return text;};
};



