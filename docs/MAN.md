# JUSTNIFFER
    Section: (8)
    Updated: March 22, 2025
## NAME
    justniffer - tcp flow sniffer  
## SYNOPSIS
    justniffer [ [-i interface] or [-f <tcpdump file>] ] 
    [-p <packet filter>]
    [-m]
    [-u or -x] 
    [ [-r] or [-l <log format>] or [-a <log format>]  ] 
    [-e <external program>]
    [-U <user> ]   
    [-n <not-found> ] 
    [-s <max concurrent tcp streams> ]  
    [-d <max concurrent IP fragments> ]
    [-F]

## Examples 
Logging network traffic in Apache like format:

    justniffer -i eth0 

Tracing tcpdump dump in Apache like format:

    justniffer -f file.cap 

Tracing TCP streams from the network:

    justniffer -i eth0 -r 

Logging network traffic in Apache like format appending response times:
    
    justniffer -i eth0 -a " %response.time" 

Logging network traffic in a customized format:

    justniffer -i eth0 -l "%source.ip%tab%dest.ip%tab%request.header.host%tab%response.time" 

## DESCRIPTION

justniffer captures reassembles and reorders TCP packets, performs IP packet defragmentation and displays the tcp flow in the standard output.
It is useful for logging network traffic in a 'standard' (web server like) or in a customized way.
It can log network services performances (e.g. web server response time , application server keep alive behaviour, etc.) .
Output format can be customized using the log format option -l (see FORMAT KEYWORDS). 
Most of them can be used for retrieving HTTP protocol informations. See EXAMPLES
 

## TRACKING PERFORMANCES
The main feature of justniffer is to analize network traffic to monitor performances. The performances related keywords are:
- %connection.time
- %idle.time.0
- %request.time
- %response.time
    - %response.time.begin
    - %response.time.end
- %idle.time.1


        +---------+                           +---------+

        |         |                           |         |

        |  Client |                           | Server  |

        |         |                           |         |

        +---------+                           +---------+

            |                                     |

            |  -----   connect syn   -------->    |----+

            |                                     |    |

            |  <------   syn/ack    --------->    |    | %connection.time

            |                                     |    |

            |  -------     ack     ---------->    |    |

            |           ESTABLISHED               |----+

            |                                     |    | %idle.time.0 

            |                                     |    |(after connection, before 

            |                                     |    | request)

            |                                     |    |

            |  ---  request/first packet  --->    |----+

            |  <------     ack     -----------    |    |

            |                                     |    |

            |  ---  request/....          --->    |    | %request.time

            |  <------     ack     -----------    |    |

            |                                     |    |

            |  ---   request/last packet  --->    |    |

            |  <------     ack     -----------    |----+--------------------+

            |                                     |    |                    |

            |                                     |    |                    |

            |                                     |    |%response.time.begin |   

            |                                     |    |                    |

            |  <--  response/first packet ----    |----+                    | response 

            |  -------     ack     ---------->    |    |                    | time

            |                                     |    |                    |

            |  <--  response/....         ----    |    |%response.time.end   |

            |  -------     ack     ---------->    |    |                    |

            |                                     |    |                    |

            |  <--  response/last packet  ----    |    |                    |

            |  -------     ack     ---------->    |----+--------------------+

            |                                     |    |

            |                                     |    |

            |                                     |    | %idle.time.1 (after response, 

            |                                     |    | before new request or close)

            |                                     |    |

            |  <------   close      --------->    |----+

            |                                     |    |

            |                                     |    |


## OPTIONS

**-i** or **--interface=<interface>** interface to listen on (e.g. eth0, en1, etc.)
Example: justniffer -i eth0
**-f** or **--filecap=<file>**tcpdump file to read from (for offline network traffic processing). It must be a pcap file (produced by network capture programs such as tcpdump or wireshark) WARNING: justniffer needs a complete dump, usually, sniffers collect just the few first (96) bytes per packet. (when using tcpdump you must specify "-s 0" option. Example:

     tcpdump -i eth0 -s 0 -w /tmp/file.cap)

Example: justniffer -f /tmp/file.cap
    -F or --force-read-pcap
    Force the reading of a pcap file also if captured with truncated packets (for example when using tcpdump without the "-s 0" option)
    -p or --packet-filter=<filter>
    packet filter (pcap filter syntax) (see pcap-filter(7))

Examples:

sniffing proxy traffic

    justniffer -i eth0 -p "tcp port 8080"


sniffing raw telnet traffic

        justniffer -i eth0 -r -p "tcp port 23"


sniffing raw pop3 traffic

        justniffer -i eth0 -r -p "tcp port 110"


sniffing  traffic from/to a specific host

        justniffer -i eth0 -r -p "host 10.10.10.2"


sniffing  HTTP traffic from/to a specific host and port

        justniffer -i eth0 -r -p "host 10.10.10.2 and tcp port 80"


**-l** or **--log-format=<format>** log format. You can specify the output string format containing reserved keyword that will be replaced with the proper value (see FORMAT KEYWORDS). If missing, the CLF (Common Log Format, used by almost all web servers) is used as default.

Example:

     justniffer -i eth0 -l "\"%request.line\"%tab%response.time"

        "POST /v2/rss/alerts?src=ffbmext2.1.034 HTTP/1.1" 0.139011
        "POST /v2/rss/network/oreste.notelli?src=ffbmext2.1.034 HTTP/1.1" 0.623382
        "GET /man_page_howto.html HTTP/1.1"       0.024437
        "GET /ig?hl=en HTTP/1.1"  0.764945
        "GET /?hl=en&tab=wv HTTP/1.1"   0.242342
        "GET /s/-yCdCsgUnsI/css/homepage_c.css HTTP/1.1"        0.071942
        "GET /vi/YUvWcegtqik/default.jpg HTTP/1.1"      0.821472

**-r** or **--raw**
show raw stream. it is a shortcut for -l %request%response

Example: justniffer -i eth0 -r

****-m or \--capture-in-the-middle****

Captures and reconstructs TCP streams in the middle (even without
    the initial connection).\
    **WARNING: it may yield unexpected results.**

**-s** or **--max-tcp-streams** max concurrent TCP stream. (default= 65536) excess will be discarded
**-d** or **--max-fragmented-ip** max concurrent fragmented IP. (default= 65536) excess will be discarded
**-u** or **--unprintable** encode as dots (.) unprintable characters ( for more control on character you should use pipelining to cat -v.

Example:

    justniffer -i eth0 -l "%request%newline%response"| cat -v
    justniffer -i eth0 -ru
    -x or --hex-encode
    encode unprintable characters in [<char hex code>] format
    Example:

    justniffer -i eth0 -rx


**-n** or **--not-found <not found string>** Not found string. It is used to replace a specified keyword when it cannot be valued because it is not found. All request.header.* and response.header.* keywords can override the "not found string" passing it as parameter. For example:

**%request.header.host()** will be replaced by the Host header value, or an empty string if Host header not found

**%request.header.host(UNKNOWN)** will be replaced by the Host header 
value, or the UNKNOWN string if Host header not found

**%request.header.host** will be replaced by the Host header value, or , if Host header not found, with  the string specified by the -n option 


Examples:

    justniffer -i eth0 -l "%request.header.connection" -n N/A  

will produce such logs:

        N/A
        N/A
        keep-alive
        close

Note: each keyword can override the "not found string" value:

    justniffer -i eth0 -l "%request.header.connection(None) %request.header.connection(-) %request.header.connection() %request.header.connection" -n N/A  

will produce such logs:

        None -  N/A
        None -  N/A
        keep-alive keep-alive keep-alive keep-alive
        close close close close

**-e** or **--execute**<external program> call the specified external program/shell script pipelining the standard output for each request/response phase You can write shell script for handling, for example, HTTP traffic
Example:

    justniffer -i eth0 -l "%request%newline%response" -e "tail -2 "

**-U** or **--user=<user>** User to impersonate when executing the program specified with the -e option, used to avoid to security exploits when running justniffer with root privileges
Example:

    justniffer -i eth0 -l "%request%newline%response" -e "grep password >> /tmp/passwords.txt"  -U guest
**-c** or **--config=<config file>** configuration file. You can specify options in a configuration file (command line options override file configuration options) using the following format specifications:
    <option> = <value>

configuration file example:

    log-format = "%request.url %request.header.host %response.code %%response.time"
    packet-filter = "tcp port 80 or tcp port 8080 or tcp port 3526"

    
## FORMAT KEYWORDS
 List of all recognized keywords:

        ### %close.time([not applicable string])

elapsed time from last response and when the connection is closed. the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %close.timestamp([format])
is replaced by the close timestamp. You can use optional format specification (see TIMESTAMP FORMAT)

### %close.timestamp2([not applicable string])
is replaced by the connection timestamp using format "seconds.microseconds" the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %connection
connection persistence indicator:
    unique: the request/response is the unique in the tcp connection
    start: the request/response is the first in the tcp connection
    last : the request/response is the last in the tcp connection
    continue : the request/response is the middle in the tcp connection

### %connection.time([not applicable string])
elapsed time for establishing the TCP connection. The "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %connection.timestamp([format])
is replaced by the connection timestamp. You can use optional format specification (see TIMESTAMP FORMAT)

### %connection.timestamp2([not applicable string])
is replaced by the connection timestamp using format "seconds.microseconds" the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %idle.time.0
elapsed time form when the connection is established and the request is started the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %idle.time.1
elapsed time form when the last response and the next request (or the connection closing) the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %response.time.begin
elapsed time form when the request and the response start the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %response.time.end
elapsed time form the response start and the response end the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %response.timestamp([format])
elapsed time for the whole response the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %dest.ip
is replaced by the destination IP address

### %dest.port
is replaced by the destination TCP port

### %source.ip
is replaced by the source IP address

### %source.port
is replaced by the source TCP port

### %request
is replaced by the the whole request ( (it is multiline and may contain unprintable characters)

### %request.timestamp([format])
is replaced by the request timestamp. You can use optional format specification (see TIMESTAMP FORMAT)

### %request.timestamp2([not applicable string])
is replaced by the request timestamp using format "seconds.microseconds" the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %request.size
is replaced by the request size (including request header size)

### %request.line
is replaced by the request line (e.g. "GET /index.html HTTP/1.1")

### %request.method
is replaced by the request method (e.g. GET, POST, HEAD)

### %request.url
is replaced by the url

### %request.protocol
is replaced by the protocol (e.g. HTTP/1.0, HTTP/1.1)

### %request.grep(<regular-expression>)
is replaced by the result of the specified regular expression applied on the whole request [Perl regular expression syntax, see perlre(1) or perl(1)]. The most nested subgroup is returned

### %request.header
is replaced by the request header (it is multiline)

### %request.header.host([not found string])
is replaced by the request Host header value. The optional "not found" string is replaced in case the keyword value was not found. if not provided the -n value or the default value "-" is used

### %request.header.user-agent([not found string])
is replaced by the request User-Agent header value. The optional "not found" string is replaced in case the keyword value was not found. if not provided the -n value or the default value "-" is used

### %request.header.accept([not found string])
is replaced by the request Accept header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.accept-language([not found string])
is replaced by the request Accept-Language header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.accept-charset([not found string])
is replaced by the request Accept-Charset header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.accept-encoding([not found string])
is replaced by the request Accept-Encoding header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.authorization([not found string])
is replaced by the request Authorization header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.connection([not found string])
is replaced by the request Connection header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.content-encoding([not found string])
is replaced by the request Content-Encoding header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.content-length([not found string])
is replaced by the request Content-Length header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.content-md5([not found string])
is replaced by the request Content-MD5 header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.cookie([not found string])
is replaced by the request Cookie header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.range([not found string])
is replaced by the request Range header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.referer([not found string])
is replaced by the request Referer header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.keep-alive([not found string])
is replaced by the request Keep-Alive header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.value(<header-name>
is replaced by the request header value (e.g. "%request.header.value(Cookie)") The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.transfer-encoding([not found string])
is replaced by the request Transfer-Encoding header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.via([not found string])
is replaced by the request Via header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.grep(<regular-expression>)
is replaced by the result of the specified regular expression applied on the request header [Perl regular expression syntax, see perlre(1) or perl(1)]. The most nested subgroup is returned (e.g. to obtain the request URL: "%request.header.grep(^[^\s]*\s*([^\s]*))"

### %response
is replaced by the while response (it is multiline and may contain unprintable characters)

### %response.timestamp([format])
is replaced by the response timestamp. You can use optional format specification (see TIMESTAMP FORMAT)

### %request.timestamp2([not applicable string]))
is replaced by the response timestamp using format "seconds.microseconds" the "not applicable" string is replaced in case the keyword value cannot be applicable. if not provided the -n value or the default value "-" is used

### %response.size
is replaced by the response size (including response the header size)

### %response.time
is replaced by the response time (difference from the request time and the time the response finish)

### %response.line
is replaced by the response line

### %response.protocol
is replaced by the response protocol

### %response.code
is replaced by the response code (e.g. 200, 404, 500, etc.)

### %response.message
is replaced by response message (e.g. OK, Not Found, Internal Server Error, etc.)

### %response.grep(<regular-expression>)
is replaced by the result of the specified regular expression applied on the whole response [Perl regular expression syntax, see perlre(1) or perl(1)]. The most nested subgroup is returned

### %response.header
is replaced by the response header (it is multiline)

### %request.header.allow([not found string])
is replaced by the request Allow header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.server([not found string])
is replaced by the response Server header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.date([not found string])
is replaced by the response Date header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.content-length([not found string])
is replaced by the response Content-Length header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.content-type([not found string])
is replaced by the response Content-Type header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.content-md5([not found string])
is replaced by the request Content-MD5 header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.content-range([not found string])
is replaced by the request Content-Range header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.content-encoding([not found string])
is replaced by the response Content-Encoding header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.content-language([not found string])
is replaced by the response Content-Language header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.transfer-encoding([not found string])
is replaced by the response Transfer-Encoding header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %%response.header.expires is replaced by the response Expires header value

### %response.header.etag([not found string])
is replaced by the response ETag header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.cache-control([not found string])
is replaced by the response Cache-Control header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.last-modified([not found string])
is replaced by the response Last-Modified header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.pragma([not found string])
is replaced by the response Pragma header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.age([not found string])
is replaced by the response Age header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.connection([not found string])
is replaced by the response Connection header value. The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.keep-alive([not found string])
is replaced by the response Keep-Alive header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.via([not found string])
is replaced by the response Via header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.vary([not found string])
is replaced by the response Vary header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.www-authenticate([not found string])
is replaced by the request WWW-Authenticate header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.accept-ranges([not found string])
is replaced by the response Accept-Ranges header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %response.header.set-cookie([not found string])
is replaced by the response Set-Cookie header value The optional "not found" string is replaced in case the keyword value was not found. If not provided the -n value or the default value "-" is used

### %request.header.value(<header-name>)

### %%response.header.value(<header-name>) is replaced by the response header value (e.g. "%request.header.value(Set-Cookie)")

### %response.header.grep(<regular-expression>)
is replaced by the result of the specified regular expression applied on the response header [Perl regular expression syntax, see perlre(1) or perl(1)]. The most nested subgroup is returned (e.g. to obtain the request URL: "%request.header.grep(^[^\s]*\s*([^\s]*))"

### %tab
is replaced by a tab

### %-
break (used for breaking keywords). For example, if you want to obtain output like this:
"0.234342                  seconds"
you must use the break keyword (%-) to mark the %tab keyword end:


"%response.time%tab%-seconds" 


### %%
is replaced by the '%' character

### %newline
is replaced by a newline

## TIMESTAMP FORMAT
Timestamp format keywords (see strftime(3) ) :

### %A
is replaced by national representation of the full weekday name.

### %a
is replaced by national representation of the abbreviated weekday name.

### %B
is replaced by national representation of the full month name.

### %b
is replaced by national representation of the abbreviated month name.

### %C
is replaced by (year / 100) as decimal number; single digits are preceded by a zero.

### %c
is replaced by national representation of time and date.

### %D
is equivalent to ``%m/%d/%y''.

### %d
is replaced by the day of the month as a decimal number (01-31).

### %E* %O*
POSIX locale extensions. The sequences %Ec %EC %Ex %EX %Ey %EY %%Od %Oe %OH %OI %Om %OM %OS %Ou %OU %OV %Ow %OW %Oy are supposed to provide alternate representations.
Additionally %OB implemented to represent alternative months names (used standalone, without day mentioned).


### %e
is replaced by the day of month as a decimal number (1-31); single digits are preceded by a blank.

### %F
is equivalent to ``%Y-%m-%d''.

### %G
is replaced by a year as a decimal number with century. This year is the one that contains the greater part of the week (Monday as the first day of the week).

### %g
is replaced by the same year as in ``%G'', but as a decimal number without century (00-99).

### %H
is replaced by the hour (24-hour clock) as a decimal number (00-23).

### %h
the same as %b.

### %I
is replaced by the hour (12-hour clock) as a decimal number (01-12).

### %j
is replaced by the day of the year as a decimal number (001-366).

### %k
is replaced by the hour (24-hour clock) as a decimal number (0-23); single digits are preceded by a blank.

### %l
is replaced by the hour (12-hour clock) as a decimal number (1-12); single digits are preceded by a blank.

### %M
is replaced by the minute as a decimal number (00-59).

### %m
is replaced by the month as a decimal number (01-12).

### %n
is replaced by a newline.

### %O*
the same as %E*.

### %p
is replaced by national representation of either "ante meridiem" or "post meridiem" as appropriate.

### %R
is equivalent to ``%H:%M''.

### %r
is equivalent to ``%I:%M:%S %p''.

### %S
is replaced by the second as a decimal number (00-60).

### %s
is replaced by the number of seconds since the Epoch, UTC (see mktime(3)).

### %T
is equivalent to ``%H:%M:%S''.

### %t
is replaced by a tab.

### %U
is replaced by the week number of the year (Sunday as the first day of the week) as a decimal number (00-53).

### %u
is replaced by the weekday (Monday as the first day of the week) as a decimal number (1-7).

### %V
is replaced by the week number of the year (Monday as the first day
of the week) as a decimal number (01-53).
If the week containing January 1 has four or more days in the new year, then it is week 1; otherwise it is the last week of the previous year, and the next week is week 1.

### %v
is equivalent to ``%e-%b-%Y''.

### %W
is replaced by the week number of the year (Monday as the first day of the week) as a decimal number (00-53).

### %w
is replaced by the weekday (Sunday as the first day of the week) as a decimal number (0-6).

### %X
is replaced by national representation of the time.

### %x
is replaced by national representation of the date.

### %Y
is replaced by the year with century as a decimal number.

### %y
is replaced by the year without century as a decimal number (00-99).

### %Z
is replaced by the time zone name.

### %z
is replaced by the time zone offset from UTC; a leading plus sign stands for east of UTC, a minus sign for west of UTC, hours and minutes follow with two digits each and no delimiter between them (common form for RFC 822 date headers).

### %+
is replaced by national representation of the date and time (the format is similar to that produced by date(1)).

### %%
is replaced by `%'.
    
## EXAMPLES
    sudo justsfniffer -i eth0 > /tmp/test.log
    sudo justsfniffer -i eth0 -l "%request.timestamp(%T %%D) - %request.header.host - %response.code - %response.time" > /tmp/test.log
    sudo justniffer -i eth0 -c config
    justniffer -f ./test.cap
    
