ACLOCAL_AMFLAGS= -I m4
AM_CPPFLAGS= $(NIDS2_INCLUDE) $(PCAP_INCLUDE) $(BOOST_CPPFLAGS) -I $(PYTHON_INCLUDE_DIR) -I ../include
LDADD=$(NIDS2_LIB) $(PCAP_LIB) $(BOOST_LDFLAGS) $(BOOST_REGEX_LDFLAGS) $(BOOST_PROGRAM_OPTIONS_LDFLAGS) $(BOOST_PYTHON_LDFLAGS) $(BOOST_REGEX_LIBS) $(BOOST_PROGRAM_OPTIONS_LIBS) $(BOOST_PYTHON_LIBS)  -l$(PYTHON_LIB) 
bin_PROGRAMS = justniffer
justniffer_SOURCES =  $(PYTHON_MODULES) main.cpp formatter.cpp utilities.cpp regex.cpp prog_read_file.cpp
justniffer_CPPFLAGS = $(AM_CPPFLAGS)
     
#lib_LTLIBRARIES = libjustniffer.la
#libjustniffer_la_SOURCES =  formatter.cpp utilities.cpp regex.cpp python.cpp read_file.cpp
#libjustniffer_la_LIBADD= $(LDADD) 
#libjustniffer_la_CPPFLAGS = $(AM_CPPFLAGS)

#echo $(HAVE_PYTHON_MODULES)
#justniffer_SOURCES+= python.cpp 
#endif
 
