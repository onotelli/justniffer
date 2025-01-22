/*
	Copyright (c) 2007 Plecno s.r.l. All Rights Reserved 
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>	
*/

#ifndef _sniffer_utilities_h
#define _sniffer_utilities_h

#include <string>
#include <exception>
#include <boost/shared_ptr.hpp>
#include <nids2.h>
#include <sys/time.h>
#include <unistd.h>
#include <utility>
using namespace std;

template< class T> class shared_obj
{
public:
	typedef boost::shared_ptr<T> ptr;
};

class common_exception : public exception
{
public:
	common_exception(const common_exception& exp): _msg (exp._msg)
	{
	}
	
	common_exception(const string& msg): _msg (msg)
	{
	}
	
	common_exception(const char* msg): _msg (msg)
	{
	}
	
	virtual const char * what () const throw ()
	{
		return _msg.c_str();
	}
	~common_exception() throw()
	{}
private:
	string _msg;
};

class invalid_pcap_file : public common_exception
{
public:
	invalid_pcap_file(const char* msg):common_exception(msg)
	{
	}
	
	invalid_pcap_file(const string& msg):common_exception(msg)
	{
	}
	
	~invalid_pcap_file() throw()
	{}
};

inline double to_double(const timeval& t)
{
	return double (t.tv_sec)+( double(t.tv_usec)/ 1000000);
}

unsigned long ip_to_ulong(char b0, char b1, char b2 , char b3);
string ip_to_str (u_long addr);
void check_pcap_file(const string& str);
bool operator < (const struct tuple4& a, const struct tuple4& b);
bool operator < (const timeval&  a, const timeval& b);
timeval operator -(const timeval& x, const timeval& y);
bool get_headers(const char* start, const char* end,  string& str);
bool get_body(const char* start, const char* end, string& str, bool header_complete);
bool get_first_line (const char* start , const char* end, string& out);
std::string timestamp(const timeval* tv, const string& frm);
void change_current_user(const char* username);

class run_as
{
public:
    run_as( const string& username);
    ~run_as();
private:
  uid_t previous_uid;
};

template <class E> void check (bool arg1, const E& e)
{
	if (!arg1)
		throw E(e);
}

#endif //_sniffer_utilities_h
