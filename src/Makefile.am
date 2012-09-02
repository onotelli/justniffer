AM_CPPFLAGS= $(NIDS2_INCLUDE) $(PCAP_INCLUDE) $(BOOST_CPPFLAGS) $(PYTHON_CPPFLAGS) -I ../include
LDADD=$(NIDS2_LIB) $(PCAP_LIB) $(BOOST_LDFLAGS) $(BOOST_REGEX_LIB) $(BOOST_PROGRAM_OPTIONS_LIB) $(BOOST_PYTHON_LIB)  $(PYTHON_LDFLAGS) 

bin_PROGRAMS = justniffer

justniffer_SOURCES =  main.cpp formatter.cpp utilities.cpp regex.cpp 

if HAVE_PYTHON_MODULES
justniffer_SOURCES+= python.cpp 
endif
 