
# Justniffer 

## Network TCP Packet Sniffer

Justniffer is a network protocol analyzer that captures network traffic and produces logs in a customized way, can emulate Apache web server log files, track response times and extract all "intercepted" files from the HTTP traffic.


## EXAMPLES

### Example 1. Retrieving http network traffic in access_log format
    $ justniffer -i eth0
output:

    192.168.2.2 - - [15/Apr/2009:17:19:57 +0200] "GET /sflogo.php?group_id=205860&type=2 HTTP/1.1" 200 0 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"
    192.168.2.2 - - [15/Apr/2009:17:20:18 +0200] "GET /search?q=subversion+tagging&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a HTTP/1.1" 200 0 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"
    192.168.2.2 - - [15/Apr/2009:17:20:07 +0200] "GET /sflogo.php?group_id=205860&type=2 HTTP/1.1" 200 0 "http://justniffer.sourceforge.net/" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid)Firefox/3.0.8)"
    192.168.2.2 - - [15/Apr/2009:17:20:18 +0200] "GET /csi?v=3&s=web&action=&tran=undefined&ei=MvvlSdjOEciRsAbY0rGpCw&e=19592,20292&rt=prt.175,xjs.557,ol.558 HTTP/1.1" 204 0 "http://www.google.it/search?q=subversion+tagging&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8 Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"
    192.168.2.2 - - [15/Apr/2009:17:20:07 +0200] "GET /HTTP/1.1" 200 0 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"

### Example 2. Like Example 1 but appending other fields,
For example http response time (see man page for a complete keyword list)

    $ justniffer -i eth0 -a " %response.time"
output:

    192.168.2.5 - - [22/Apr/2009:22:27:36 +0200] "GET /sflogo.php?group_id=205860&type=2 HTTP/1.1" 200 0 "http://justniffer.sourceforge.net/" "Mozilla/5.0 (X11;U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)" 0.427993 
    192.168.2.5 - - [22/Apr/2009:22:27:50 +0200] "GET /complete/search?output=firefox&client=firefox&hl=en-US&q=add+e HTTP/1.1" 200 140 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"0.294897 
    192.168.2.5 - - [22/Apr/2009:22:27:51 +0200] "GET /complete/search?output=firefox&client=firefox&hl=en-US&q=add+a HTTP/1.1" 200 128 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)"0.266929 
    192.168.2.5 - - [22/Apr/2009:22:27:21 +0200] "GET /extern_js/f/CgJlbiswCjgVLCswDjgFLCswFjgJLCswFzgBLCswGDgDLCswITgWLCswJTjJiAEsKzAmOAQsKzAnOAAs/-wB3HvFrpXA.js HTTP/1.1" 304 0 "http://www.google.com/search?q=gnusticker&hl=en&safe=off&start=20&sa=N" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009032711 Ubuntu/8.10 (intrepid) Firefox/3.0.8)" 2.025879

### Example 3. Capture all tcp traffic
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

### Example 4. Define a completely custom log format

    $ justniffer -i eth0 -l "%request.timestamp %source.ip %dest.ip %request.header.host %request.url" 

output:

    06/28/11 13:30:48 192.168.2.2 72.14.221.118 i1.ytimg.com /vi/TjSk6CVN5LY/default.jpg 
    06/28/11 13:30:47 192.168.2.2 72.14.221.118 i2.ytimg.com /vi/iw_nzfm1Vts/default.jpg 
    06/28/11 13:30:47 192.168.2.2 216.34.181.71 static.sourceforge.net /css/phoneix/jquery.cluetip.php?secure=0 
    06/28/11 13:30:48 192.168.2.2 216.34.181.71 static.sourceforge.net /sfx.js 
    06/28/11 13:30:49 192.168.2.2 216.34.181.71 static.sourceforge.net /include/coremetrics/v40/eluminate.js 
    06/28/11 13:30:51 192.168.2.2 199.93.61.126 c.fsdn.com /sf/images/phoneix/grad_white_dual_100.png 

### Example 5. Read from a capture file
NOTE: capture file must be performed with unlimited snaplen for catching whole packets. Justniffer can work only works on pcap files with whole packets.
tcpdump command example: tcpdump -w /tmp/file.cap -s0 -i ath0

    $ justniffer -f /file.cap


see  [project site](https://onotelli.github.io/justniffer/)
