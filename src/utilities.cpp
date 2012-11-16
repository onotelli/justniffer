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
#include <vector>
#include <iostream>
#include <unistd.h>
#include <pwd.h>

using namespace std;

template <class T> void print (T t)
{
	cout <<t <<"\n";
}
#define	TH_FIN	0x01
#define	TH_SYN	0x02
#define	TH_RST	0x04
#define	TH_PUSH	0x08
#define	TH_ACK	0x10
#define	TH_URG	0x20
#define	TH_ECE	0x40
#define	TH_CWR	0x80
#define	TH_FLAGS	(TH_FIN|TH_SYN|TH_RST|TH_ACK|TH_URG|TH_ECE|TH_CWR)

extern "C" void tcp_flags(char* buffer, int flag)
{
    vector<string> strings;
    string result;
    if (flag & TH_FIN)
        strings.push_back("fin");
    if (flag & TH_SYN)
        strings.push_back("syn");
    if (flag & TH_RST)
        strings.push_back("rst");
    if (flag & TH_PUSH)
        strings.push_back("push");
    if (flag & TH_ACK)
        strings.push_back("ack");
    if (flag & TH_URG)
        strings.push_back("urg");
    if (flag & TH_ECE)
        strings.push_back("exe");
    if (flag & TH_CWR)
        strings.push_back("cwr");
    //
    bool first = true;
    string sep;
    for (vector<string>::iterator it = strings.begin(); it != strings.end(); it++)
    {
        if (first)
            sep="";
        else
            sep="|";
        result+=sep+*it;
        first= false;
    }
    sprintf(buffer, result.c_str());
}
/*
{
#  define TH_FIN        0x01
#  define TH_SYN        0x02
#  define TH_RST        0x04
#  define TH_PUSH       0x08
#  define TH_ACK        0x10
#  define TH_URG        0x20

    char fin[6];
    char syn[6];
    char rst[6];
    char push[6];
    char ack[6];
    char urg[6];
    
    
    if (flag & TH_FIN)
        sprintf(fin, "FIN");
    else
        sprintf(fin, " ");
        
    if (flag & TH_SYN)
        sprintf(syn, "SYN");
    else
        sprintf(syn, " ");
        
    if (flag & TH_RST)
        sprintf(rst, "RST");
    else
        sprintf(rst, " ");
        
    if (flag & TH_PUSH)
        sprintf(push, "PUSH");
    else
        sprintf(push, " ");
        
    if (flag & TH_ACK)
        sprintf(ack, "ACK");
    else
        sprintf(ack, " ");
        
    if (flag & TH_URG)
        sprintf(urg, "URG");
    else
        sprintf(urg, " ");
    
    printf(syn);
    sprintf(buffer, "%s%s%s%s%s%s%s", syn, ack, push, fin, urg, rst);
#  define TH_PUSH       0x08
#  define TH_ACK        0x10
#  define TH_URG        0x20
}*/

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

void check_pcap_file(const string& str) throw (invalid_pcap_file)
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
	static char tstr[32];
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


