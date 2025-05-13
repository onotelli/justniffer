
# Justniffer 

[EXTENDING](EXTENDING) [MAN](MAN)

## Network TCP Packet Sniffer

Justniffer is a network protocol analyzer that captures network traffic and produces logs in a customized way, can emulate Apache web server log files, track response times and extract all "intercepted" files from the HTTP traffic.

Additionally, Justniffer provides insights into connection behavior, including how connections are reused for keep-alive sessions, identifying whether the client or server closes the connection, and analyzing idle times.

It lets you interactively trace tcp traffic from a live network or from a previously saved capture file. Justniffer's native capture file format is libpcap format, which is also the format used by tcpdump and various other tools.

It is highly customizable, especially through the use of Python handler classes, allowing you to tailor its functionality to specific needs

### Reliable TCP Flow Rebuilding

The main Justniffer's feature is the ability to handle all those complex low level protocol issues and retrieve the correct flow of the TCP/IP traffic: IP fragmentation, TCP retransmission, reordering. etc. It uses portions of Linux kernel source code for handling all TCP/IP stuff. Precisely, it uses a slightly modified version of the libnids libraries that already include a modified version of Linux code in a more reusable way.

### Optimized for "Request / Response" protocols. It is able to track server response time

Justniffer was born as tool for helping in analyzing performance problem in complex network environment when it becomes impractical to analyze network captures solely using wireshark. It will help you to quickly identify the most significant bottlenecks analyzing the performance at "application" protocol level.

In very complex and distributed systems is often useful to understand how communication takes place between different components, and when this is implemented as a network protocol based on TCP/IP (HTTP, JDBC, RTSP, SIP, SMTP, IMAP, POP, LDAP, REST, XML-RPC, IIOP, SOAP, etc.), justniffer becomes very useful. Often the logging level and monitoring systems of these systems does not report important information to determine performance issues such as the response time of each network request. Because they are in a "production" environment and cannot be too much verbose or they are in-house developed applications and do not provide such logging.

Other times it is desirable to collect access logs from web services implemented on different environments (various web servers, application servers, python web frameworks, etc.) or web services that are not accessible and therefore traceable only on client side.

Ideally, an egress proxy should be active to monitor network traffic. However, there are cases where a proxy is unavailable, needs to be monitored itself, or is impractical to deploy in production environments - especially while troubleshooting network traffic

Justniffer can capture traffic in promiscuous mode so it can be installed on dedicated and independent station within the same network "collision domain" of the gateway of the systems that must be analyzed, collecting all traffic without affecting the system performances and requiring invasive installation of new software in production environments.

###  Can rebuild and save HTTP content on files

The robust implementation for the reconstruction of the TCP flow turns it in a multipurpose sniffer.

HTTP sniffer
LDAP sniffer
SMTP sniffer
SIP sniffer
password sniffer
justniffer can also be used to retrieve files sent over the network.


### It is extensible

Can be extended by external scripts.


-see  [EXTENDING](EXTENDING)


### Features Summary

- Reliable TCP flow rebuilding: it can reorder, reassemble tcp segments and ip fragments using portions of the Linux kernel code
- Logging text mode can be customized
- Extensibility by any executable, such as bash, python, perl scripts, ELF executable, etc.
- Performance measurement it can collect many information on performances: connection time, close time, request time , response time, close time, etc.


## TRACKING PERFORMANCES

 The main feature of justniffer is to analize network traffic to monitor 
 performances. The performances related keywords are:
  **%connection.time**
  **%idle.time.0**
  **%request.time**
  **%response.time**
    **%response.time.begin**
    **%response.time.end**
  **%idle.time.1**



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

        |  <------     ack     -----------    |----+---------------------+

        |                                     |    |                     |

        |                                     |    |                     |

        |                                     |    |%response.time.begin |   

        |                                     |    |                     |

        |  <--  response/first packet ----    |----+                     | response 

        |  -------     ack     ---------->    |    |                     | time

        |                                     |    |                     |

        |  <--  response/....         ----    |    |%response.time.end   |

        |  -------     ack     ---------->    |    |                     |

        |                                     |    |                     |

        |  <--  response/last packet  ----    |    |                     |

        |  -------     ack     ---------->    |----+---------------------+

        |                                     |    |

        |                                     |    |

        |                                     |    | %idle.time.1 (after response, 

        |                                     |    | before new request or close)

        |                                     |    |

        |  <------   close      --------->    |----+

        |                                     |    |

        |                                     |    |
 

## INSTALL

Be sure you have installed third-party tools and libraries:

- autotools
- make
- libc6
- libpcap0.8
- g++                         
- gcc 
- libboost-iostreams          
- libboost-program-options
- libboost-regex
- libboost-thread
- bash-completion
- libboost-python (optional)
 

unpacked the source package, type:

    $ ./configure 
    $ make 
    $ make install

## Install on Ubuntu

    sudo apt install software-properties-common
    sudo add-apt-repository ppa:oreste-notelli/ppa
    sudo apt update
    sudo apt install justniffer

## Install on Debian

download the .deb file from 
[https://github.com/onotelli/justniffer/releases](https://github.com/onotelli/justniffer/releases)
and install it with:

    sudo apt install ./justniffer_<version>.deb

---
## EXAMPLES

<br>
## Example 1. Retrieving http network traffic in access_log format
    $ justniffer -i eth0

output:

    192.168.2.2 - - [15/Apr/2009:17:19:57 +0200] "GET /sflogo.php?group_id=205860&type=2 HTTP/1.1" 200 0 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"
    192.168.2.2 - - [15/Apr/2009:17:20:18 +0200] "GET /search?q=subversion+tagging&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a HTTP/1.1" 200 0 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"
    192.168.2.2 - - [15/Apr/2009:17:20:07 +0200] "GET /sflogo.php?group_id=205860&type=2 HTTP/1.1" 200 0 "http://justniffer.sourceforge.net/" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid)Firefox/3.0.8)"
    192.168.2.2 - - [15/Apr/2009:17:20:18 +0200] "GET /csi?v=3&s=web&action=&tran=undefined&ei=MvvlSdjOEciRsAbY0rGpCw&e=19592,20292&rt=prt.175,xjs.557,ol.558 HTTP/1.1" 204 0 "http://www.google.it/search?q=subversion+tagging&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8 Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"
    192.168.2.2 - - [15/Apr/2009:17:20:07 +0200] "GET /HTTP/1.1" 200 0 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"


<br>
## Example 2. Like Example 1 but appending other fields,
For example http response time (see man page for a complete keyword list)

    $ justniffer -i eth0 -a " %response.time"

output:

    192.168.2.5 - - [22/Apr/2009:22:27:36 +0200] "GET /sflogo.php?group_id=205860&type=2 HTTP/1.1" 200 0 "http://justniffer.sourceforge.net/" "Mozilla/5.0 (X11;U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)" 0.427993 
    192.168.2.5 - - [22/Apr/2009:22:27:50 +0200] "GET /complete/search?output=firefox&client=firefox&hl=en-US&q=add+e HTTP/1.1" 200 140 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"0.294897 
    192.168.2.5 - - [22/Apr/2009:22:27:51 +0200] "GET /complete/search?output=firefox&client=firefox&hl=en-US&q=add+a HTTP/1.1" 200 128 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"0.266929 
    192.168.2.5 - - [22/Apr/2009:22:27:21 +0200] "GET /extern_js/f/CgJlbiswCjgVLCswDjgFLCswFjgJLCswFzgBLCswGDgDLCswITgWLCswJTjJiAEsKzAmOAQsKzAnOAAs/-wB3HvFrpXA.js HTTP/1.1" 304 0 "http://www.google.com/search?q=gnusticker&hl=en&safe=off&start=20&sa=N" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)" 2.025879

<br>
## Example 3. Capture all tcp traffic
(add -u or -x options to encode unprintable characters):

    $ justniffer -i eth0 -r

output:

    GET /doc/maint-guide/ch-upload.en.html HTTP/1.1
    Host: www.debian.org
    User-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8)
    Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8
    Accept:
    text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en,it;q=0.5
    Accept-Encoding: gzip,deflate
    Accept-Charset: UTF-8,*
    Keep-Alive: 300
    Connection: keep-alive
    Referer: http://www.debian.org/doc/maint-guide/
    If-Modified-Since: Wed, 22 Apr 2009 19:36:31 GMT
    If-None-Match: "400d604-3014-46829e160adc0"
    Cache-Control: max-age=0

    HTTP/1.1 304 Not Modified
    Date: Wed, 22 Apr 2009 20:38:51 GMT
    Server: Apache
    Connection: Keep-Alive
    Keep-Alive: timeout=15, max=100
    ETag: "400d604-3014-46829e160adc0"
    Expires: Thu, 23 Apr 2009 20:38:51 GMT
    Cache-Control: max-age=86400

<br>

## Example 4. Define a completely custom log format

    $ justniffer -i eth0 -l "%request.timestamp %source.ip %dest.ip %request.header.host %request.url" 

output:

    06/28/11 13:30:48 192.168.2.2 72.14.221.118 i1.ytimg.com /vi/TjSk6CVN5LY/default.jpg 
    06/28/11 13:30:47 192.168.2.2 72.14.221.118 i2.ytimg.com /vi/iw_nzfm1Vts/default.jpg 
    06/28/11 13:30:47 192.168.2.2 216.34.181.71 static.sourceforge.net /css/phoneix/jquery.cluetip.php?secure=0 
    06/28/11 13:30:48 192.168.2.2 216.34.181.71 static.sourceforge.net /sfx.js 
    06/28/11 13:30:49 192.168.2.2 216.34.181.71 static.sourceforge.net /include/coremetrics/v40/eluminate.js 
    06/28/11 13:30:51 192.168.2.2 199.93.61.126 c.fsdn.com /sf/images/phoneix/grad_white_dual_100.png 

<br>

## Example 5. Read from a capture file
NOTE: capture file must be performed with unlimited snaplen for catching whole packets. Justniffer can work only works on pcap files with whole packets.
tcpdump command example: tcpdump -w /tmp/file.cap -s0 -i ath0

    $ justniffer -f /file.cap

<br>
## Example 6. Parameters for setting a more precise formatting
Many keyword has parameters for setting a more precise formatting:

    $ justniffer -i eth0 -l "%request.timestamp %request.header.host %request.url %response.time" 
output:

    06/28/11 13:39:40 static.sourceforge.net /css/phoneix/print.css?secure=0&20080417-1657 0.162620

you can specifying timestamp formatting

    $ justniffer -i eth0 -l "%request.timestamp (%B %d %Y %H:%M:%S) %request.header.host %request.url %response.time"

output:

    June 28 2009 13:39:40 static.sourceforge.net /css/phoneix/print.css?secure=0&20080417-1657 0.162620

or to print the string NoHostFound if the %request.header.host cannot be valued

    $ justniffer -i eth0 -l "%request.timestamp %request.header.host (NoHostFound)%request.url %response.time" 

output:

    06/28/11 15:10:28 www.google.com /ig?hl=en 0.116146
    06/28/11 15:10:28 NoHostFound/ig?hl=en 0.116146
many keywords have their own formatting string. A generic option ( -n) can be used for setting a default "not found" string: a string that must replace the keyword if it cannot be valued. for example if request.header.[headername] is not found or if connection.time cannot be applicable. Anyway, if a "no found" string is provided as keyword parameter (for those that expect it), it will override the -n option

    $ justniffer -i eth0 -l "%request.timestamp %request.header.host(NoHostFound) %request.header.host %request.url %response.time" -n N/A

output:
    06/28/11 15:10:28 www.google.com www.google.com/ig?hl=en 0.116146
    06/28/11 15:10:28 NoHostFound N/A/ig?hl=en 0.116146 

<br>

## Example 7. Capture only http traffic
the -p option let you to specify a tcpdump compatible filter (see pcap-filter(7)): "port 80 or port 8080" capture only http traffic (usually using tcp port 80 and 8080)

    $ justniffer -i eth0 -r -p "port 80 or port 8080"

<br>
## Example 8. Extend with an external executable
the -e option let you to specify an external executable (usually a script) to which , for every log, the output will be redirect to. If you want to perform complex extraction operations, you can write your own script that will receive from the standard input all content specified by the -l option. A complete ad useful example is provided with justniffer-grab-http-traffic
    $ justniffer -l "%response" -e ./myscript.sh -i ath0

myscript.sh
      
        
    #!/bin/bash
    # myscript.sh 
    # example script (print all lines containing "href" string)

    while read inputline
    do 
    anchors=`echo "$inputline" | grep href`
    if [ "$anchors" != "" ]; then
    echo $anchors;
    fi;
    done

      

<br>
    
## Example 9. Capture smtp traffic (usually using tcp port 25)
    $ justniffer -i eth0 -r -p "port 25"

output:
      
            
    220 plecno.com ESMTP Postfix (Ubuntu)

    EHLO unknown.localnet
    250-plecno.com       
    250-PIPELINING       
    250-SIZE             
    250-VRFY             
    250-ETRN             
    250-STARTTLS         
    250-ENHANCEDSTATUSCODES
    250-8BITMIME           
    250 DSN                

    MAIL FROM:<xxxx.xxxx@xxx.xxx> SIZE=1079
    RCPT TO:<yyyyy.xxxx@yyyy.xxx>             
    DATA                                           
    250 2.1.0 Ok                                   
    250 2.1.5 Ok                                   
    354 End data with <CR><LF>.<CR><LF>        


    From: Oreste Notelli <xxxx.xxxx@xxx.xxx>
    Organization: Plecno
    To: yyyyy.xxxx@yyyy.xxx
    Subject: test
    Date: Wed, 22 Apr 2009 22:46:16 +0200
    User-Agent: KMail/1.11.2 (Linux/2.6.27-8-generic; KDE/4.2.2; i686;
    ; )
    MIME-Version: 1.0
    Content-Type: multipart/alternative;
    boundary="Boundary-00=_ZI47J3FTNXn+25g"
    Content-Transfer-Encoding: 7bit
    Content-Disposition: inline
    Message-Id: <200904222246.17292.xxxx.xxxx@xxx.xxx>

    --Boundary-00=_ZI47J3FTNXn+25g
    Content-Type: text/plain;
    charset="us-ascii"
    Content-Transfer-Encoding: 7bit

    test

    --Boundary-00=_ZI47J3FTNXn+25g
    Content-Type: text/html;
    charset="us-ascii"
    Content-Transfer-Encoding: 7bit

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"
    "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html>
    <head>
    <meta name="qrichtext" content="1" />
    <style type="text/css">p, li { white-space: pre-wrap;
    }</style>
    </head>
    <body style=" font-family:'DejaVu Sans'; font-size:8pt;
    font-weight:400; font-style:normal;">
    <p>
    test
    </p>
    </body>
    </html>
    --Boundary-00=_ZI47J3FTNXn+25g--
    .
    250 2.0.0 Ok: queued as 33E7235C21A

    QUIT
    221 2.0.0 Bye

      

    
<br>
## Example 10. Trace performances
The following keywords are used to obtain logs that give an overview on the performance of services based on HTTP protocol measuring connection time, response time, tcp connection timeouts, keep alive requests, etc. (see man for more information)

    $ sudo justniffer -i eth0 -u -p "port 80 or port 8080" -l "%request.header.host %request.url %connection.time %idle.time.0  %request.time %response.time.begin %response.time.end %idle.time.1 %connection %close.originator"

<br>
## Example 11. Grep keywords
The "grep keywords"can be used to capture portions of text using regular expressions. In this example we want to collect:

the url from the request header by the regular expression [^\s]*[\s]*([^\s]*)
and the content type from the response header by the regular expression Content-Type:(\s)*([^\r]*)

    $ sudo justniffer -l "%request.header.grep([^\s]*[\s]*([^\s]*)) %response.header.grep(Content-Type:(\s)*([^\r]*)) %source.ip" -i eth0

output:

    / text/html 192.168.10.2
    /plecno_res/src/effects.js application/javascript 192.168.10.2
    /plecno_res/src/slider.js application/javascript 192.168.10.2
    /plecno_res/src/effects.js application/javascript 192.168.10.2
    /plecno_res/src/builder.js application/javascript 192.168.10.2
    /plecno_res/src/effects.js application/javascript 192.168.10.2

<br>
## Example 12. capture tcp traffic without the 3-way handshake (capture in the middle)
Justniffer usually does not capture traffic if it starts after a connection has already been established. It was primarily designed to measure the nature and timing of TCP connections, meaning it may lack sufficient information to retrieve certain details without the initial 3-way handshake packets (e.g., client IP/port, connection reuse, etc.)

However, in some cases, it can still be useful to trace traffic even without these precise details, so use it with an understanding of what you are obtaining.

You can use the flag **-m** or **--capture-in-the-middle** to enable capturing in the middle of a connection.

**WARNING**: it may yield unexpected results


    $ sudo justniffer -i eth0 -m -r -u

see [MAN](MAN)
