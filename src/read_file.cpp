#include "python.h"
#include <iostream>
#include "utilities.h"
#include <map>
#include <nids2.h>
#include "read_file.h"

void read_file(string filename, string capture_string)
{
    parser p;
    nids_params.pcap_timeout=10;
	nids_params.tcp_workarounds=1;
    nids_params.n_tcp_streams=65535;
    nids_params.n_hosts= 65535;
    nids_params.filename=(char*)filename.c_str();
    nids_chksum_ctl chksumctl[1];
    chksumctl[0].netaddr = ip_to_ulong(0,0,0,0);
    chksumctl[0].mask = ip_to_ulong(0,0,0,0);
    chksumctl[0].action = NIDS_DONT_CHKSUM;
    union
	{
		  void (*func) (struct tcp_stream *ts, void **yoda, struct timeval* t, unsigned char* packet);
		  void* ptr_nids_handler;
		  
	}un;
	un.func =parser::nids_handler;
  	nids_register_tcp(un.ptr_nids_handler);

    nids_register_chksum_ctl(chksumctl, 1);
    
    if (capture_string.empty())
        nids_params.pcap_filter = NULL;
    else
        nids_params.pcap_filter = (char*)capture_string.c_str();
    //nids_run();
        
} 
