justnifferpythoncodedir = $(PYTHONCODEDIR)
justnifferpythoncode_DATA = http_parser.py common.py



bin_SCRIPTS = justniffer-grab-http-traffic
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = $(justnifferpythoncode_DATA)

do_subst = python create_scripts justniffer-grab-http-traffic.in justniffer-grab-http-traffic $(PYTHONCODEDIR); chmod a+x justniffer-grab-http-traffic; chmod a+x  http_parser.py


justniffer-grab-http-traffic : justniffer-grab-http-traffic.in Makefile
	$(do_subst)

install-data-hook:
	chmod a+x  $(DESTDIR)$(PYTHONCODEDIR)/http_parser.py
