/*
	Copyright (c) 2007 Plecno s.r.l. All Rights Reserved 
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>	
*/

#include "utilities.h"
#include <pcap.h>
#include <fstream>
#include <sstream>

#include <iostream>
#include <unistd.h>
#include <pwd.h>

using namespace std;

template <class T> void print (T t)
{
	cout <<t <<"\n";
}

unsigned long ip_to_ulong(char b0, char b1, char b2 , char b3)
{
	unsigned long val ;
	unsigned char* p=(unsigned char*)&val;
	p[0] = b0;
	p[1] = b1;
	p[2] = b2;
	p[3] = b3;
	return val;
}

void check_pcap_file(const string& str) 
{
	char errbuff[4096];
	pcap_t * p = pcap_open_offline(str.c_str(), errbuff);
	if (p)
	{
		pcap_close(p);
	}
	else
	{
		throw invalid_pcap_file(string("invalid pcap file: ").append(errbuff));
	}
	struct pcap_file_header hdr;
	ifstream capstream (str.c_str(), ios_base::binary);
	capstream.read(reinterpret_cast<char*> (&hdr), sizeof(hdr));
	if (capstream.good())
	{
		if (hdr.snaplen < 65535)
		{
			stringstream ss;
			ss<<hdr.snaplen;
			throw invalid_pcap_file(string ("invalid pcap file snaplen: ").append(ss.str()).append(". Snaplen must be set to 0 (look at tcpdump -s snaplen documentation or use the -F option"));		
		}
	}
	else
	{
		throw invalid_pcap_file("invalid pcap file");
	}
}

string ip_to_str (u_long addr)
{
	stringstream ss;
	u_char* p = (u_char *)&addr;
	ss << int(p[0] & 255)<<"."<<int (p[1] & 255)<<"."<<int (p[2] & 255)<<"."<<int (p[3] & 255);
	return ss.str();
}

bool operator < (const struct tuple4& a, const struct tuple4& b)
{
	if (a.source<b.source)
		return true;
	if (a.source>b.source)
		return false;
	if (a.dest<b.dest)
		return true;
	if (a.dest>b.dest)
		return false;
	if (a.saddr<b.saddr)
		return true;
	if (a.saddr>b.saddr)
		return false;
	if (a.daddr<b.daddr)
		return true;
	if (a.daddr>b.daddr)
		return false;
	return false;	
	
}
bool operator < (const timeval& a, const timeval& b)
{
	if (a.tv_sec <b.tv_sec)
		return true;
	if (a.tv_sec >b.tv_sec)
		return false;
	if (a.tv_usec <b.tv_usec )
		return true;
	if (a.tv_usec > b.tv_usec )
		return false;
	return false;
}
bool get_first_line (const char* start , const char* end, string& out)
{
	bool complete = false;
	for (const char* it = start; it != end; it++)
	{
		if (*it == 13)
		{
			complete = true;
			break;
		}
		out+=*it;
	}
	return complete;
}

bool get_headers(const char* start, const char* end,  string& str)
{
	int counter = 0;
	bool complete = false;
	for (const char* it = start; it != end; it++)
	{
		if (*it == 13)
			counter++;
		else
			if (counter && (*it !=10))
				counter = 0;
		if (counter >=2)
		{
			complete = true;
			break;
		}
		str+=*it;
	}
	return complete;
}

bool get_body(const char* start, const char* end, string& str, bool headers_complete)
{
	int counter = 0;

    // Iterate through the data between start and end
    for (const char* it = start; it != end; ++it)
    {
        // Process headers first (headers end with double CRLF, i.e., "\r\n\r\n")
        if (!headers_complete)
        {
            // Detect a CRLF sequence (0x0D 0x0A) indicating the end of a header line
            if (*it == 13)  // CR (Carriage Return)
            {
                counter++;
            }
            else if (counter && *it != 10)  // LF (Line Feed)
            {
                counter = 0;
            }
            if (counter >= 2)  // Double CRLF
            {
                headers_complete = true;  // Mark headers as complete
				it += 2;  // Skip the double CRLF
				if (it >= end){
					break;
				}
                //str += "\r\n\r\n";  // Add the double CRLF to indicate end of headers
            }
        }

        if (headers_complete)
        {
            str += *it;  // Append the character to the response body

        }
    }

    // If we have completed the entire response (headers and body), return true

    return headers_complete;
}


timeval operator -(const timeval& x, const timeval& y)
{
	timeval t1 = x;
	timeval t2 = y;

	if (t1.tv_usec < t2.tv_usec) {
    int nsec = (t2.tv_usec - t1.tv_usec) / 1000000 + 1;
    t2.tv_usec -= 1000000 * nsec;
    t2.tv_sec += nsec;
  }
  if (t1.tv_usec - t2.tv_usec > 1000000) {
    int nsec = (t1.tv_usec - t2.tv_usec) / 1000000;
    t2.tv_usec += 1000000 * nsec;
    t2.tv_sec -= nsec;
  }

  /* Compute the time remaining to wait.
     tv_usec is certainly positive. */
  timeval result;
  result.tv_sec = t1.tv_sec - t2.tv_sec;
  result.tv_usec = t1.tv_usec - t2.tv_usec;
  return result;
}

string timestamp(const timeval* tv, const string &frm)
{
	char tstr[32];
	struct tm *t, gmt;
	time_t tt = tv->tv_sec;
	int days, hours, tz, len;
	
	gmt = *gmtime(&tt);
	t = localtime(&tt);
	
	days = t->tm_yday - gmt.tm_yday;
	hours = ((days < -1 ? 24 : 1 < days ? -24 : days * 24) +
		 t->tm_hour - gmt.tm_hour);
	tz = hours * 60 + t->tm_min - gmt.tm_min;
	
	len = strftime(tstr, sizeof(tstr), frm.c_str(), t);
	if (len < 0 || len > (signed)(sizeof(tstr) - 5))
		return (NULL);
	return (tstr);
}

void change_current_user(const char* username)
{
      uid_t userid;
      struct passwd* pwd;
      pwd = getpwnam(username);
      if (pwd)
      {
	username = pwd->pw_name;
	userid = pwd->pw_uid;
	seteuid(userid);
      }
}

run_as::run_as( const string& username)
{
      struct passwd* pwd;
      previous_uid = getuid();
      pwd = getpwnam(username.c_str());
      if (pwd)
	setuid( pwd->pw_uid);
}

run_as::~run_as()
{
    setuid( previous_uid);
}


