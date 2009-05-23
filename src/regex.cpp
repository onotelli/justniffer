/*
	Copyright (c) 2007 Plecno s.r.l. All Rights Reserved 
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>	
*/

#include "regex.h"

using namespace std;

string regex(const boost::regex& re, const string& text)
{
	string result;
	boost::smatch what;
	if (boost::regex_search(text, what, re))
	for (boost::smatch::const_iterator it = what.begin(); it != what.end(); it++)
	{
		result.assign(*it);
	}
	return result;
}

void regex_handler_base::append(std::basic_ostream<char>& out, const timeval*)
{
	string res = ::regex(_re, get_text());
	if (res.empty())
		out << _not_found;
	else
		out<<res;
}