/*
	Copyright (c) 2007 Plecno s.r.l. All Rights Reserved
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>

	Contributors: Benet Leong <benetleong@gmail.com>

*/

#include "config.h"
#include <boost/program_options.hpp>
#include <boost/iostreams/filtering_stream.hpp>
#include <boost/algorithm/string/join.hpp>
#include <boost/thread.hpp>
#include <boost/asio.hpp>
#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <nids2.h>
#include "formatter.h"
#include "utilities.h"

using namespace std;
namespace po = boost::program_options;
namespace pos = boost::iostreams;
static void show_usage(parser &p);
static const char *copyrights = PACKAGE_NAME " " JUSTNIFFER_VERSION "\nWritten by Oreste Notelli <oreste.notelli@plecno.com>\nCopyright (c) 2007- " JUSTNIFFER_YEAR " Plecno s.r.l.";
static po::options_description desc(string(copyrights).append("\n\nUsage").c_str());
static void show_version()
{
	cout << copyrights << "\n";
}

ostream &print_error(const string &arg)
{
	cerr << "\nERROR: " << arg;
	return cerr;
}
ostream &print_error(const char *arg)
{
	cerr << "\nERROR: " << arg;
	return cerr;
}

ostream &print_warning(const string &arg)
{
	cerr << "\nWARNING: " << arg;
	return cerr;
}

ostream &print_warning(const char *arg)
{
	cerr << "\nWARNING: " << arg;
	return cerr;
}

static void null_syslog(int type, int errnum, struct ip *iph, void *data)
{
}

const char *help_cmd = "help";
const char *filecap_cmd = "filecap";
const char *interface_cmd = "interface";
const char *logformat_cmd = "log-format";
const char *append_logformat_cmd = "append-log-format";
const char *config_cmd = "config";
const char *user_cmd = "user";
const char *packet_filter_cmd = "packet-filter";
const char *tcp_timeout_cmd = "tcp-timeout";
const char *max_concurrent_tcp_stream = "max-tcp-streams";
const char *max_fragmented_ip_hosts = "max-fragmented-ip";
const char *version_cmd = "version";
const char *uprintable_cmd = "unprintable";
const char *uprintable_cmd_ext = "hex-encode";
const char *raw_cmd = "raw";
const char *handle_truncated_cmd = "truncated";
const char *not_found_string = "not-found";
const char *execute_cmd = "execute";
const char *default_packet_filter = "";
const char *default_format = "%source.ip - - [%request.timestamp(%d/%b/%Y:%T %z)] \"%request.line\" %response.code %response.header.content-length(0) \"%request.header.referer()\" \"%request.header.user-agent()\"";
const char *raw_format = "%request%response";
const char *default_not_found = "-";
const char *force_read_pcap = "force-read-pcap";
const char *capture_in_the_middle = "capture-in-the-middle";
const char *python_function = "python";
const char *no_newline = "no-newline";

typedef vector<string>::const_iterator args_type;
bool check_conflicts(const po::variables_map &vm, const vector<string> &arguments)
{
	vector<string> founds;
	for (args_type it = arguments.begin(); it != arguments.end(); it++)
	{
		string a = *it;
		po::variable_value arg = vm[*it];
		if (!arg.empty())
			founds.push_back(*it);
	}
	if (founds.size() > 1)
	{
		string msg = "options ";
		int counter = 0;
		for (args_type it2 = founds.begin(); it2 != founds.end(); it2++)
		{
			string a = *it2;
			if (counter != 0)
				msg.append(", ");
			msg.append(a);
			counter++;
		}
		print_error(msg.append(" are conflicting\n"));
		return true;
	}
	return false;
}

static int max_concurrent_tcp_stream_v;
static int max_fragmented_ip_hosts_v;

boost::asio::io_service io_service;
boost::asio::signal_set signals(io_service, SIGINT);
boost::thread signal_thread;



void signal_handler(const boost::system::error_code& error, int signal_number) {
    if (!error) {
		nids_exit();
        io_service.stop();
    }
}

void run_signal_service() {
    signals.async_wait(signal_handler);
    io_service.run();
}

int main(int argc, char *argv[])
{
	parser p;
	try
	{
		desc.add_options()(help_cmd, "command line description")
		(string(version_cmd).append(",V").c_str(), "version")
		(string(filecap_cmd).append(",f").c_str(), po::value<string>(), "input file in 'tcpdump capture file format' (e.g. produced by tshark or tcpdump)")
		(string(interface_cmd).append(",i").c_str(), po::value<string>(), "network interface to listen on (e.g. eth0, en1, etc.)")
		(string(logformat_cmd).append(",l").c_str(), po::value<vector<string>>()->multitoken(), string("log format (see FORMAT KEYWORDS). If missing the CommonLog (apache access log) format will ne used. See man page for further infos\nIt is equivalent to \n").append(default_format).c_str())
		(string(append_logformat_cmd).append(",a").c_str(), po::value<string>(), "append log format (see FORMAT KEYWORDS) to the default apache log format.")
		(string(config_cmd).append(",c").c_str(), po::value<string>(), "configuration file")
		(string(user_cmd).append(",U").c_str(), po::value<string>(), string("user to impersonate when executing the command specified by the \"").append(execute_cmd).append("\" option").c_str())
		(string(execute_cmd).append(",e").c_str(), po::value<string>(), "execute the specified command every request/response phase")
		(string(packet_filter_cmd).append(",p").c_str(), po::value<vector<string>>()->multitoken(), "packet filter (tcpdump filter syntax)")
		(string(uprintable_cmd).append(",u").c_str(), "encode as dots (.) unprintable characters")
		(string(handle_truncated_cmd).append(",t").c_str(), "handle truncated streams (not correctly closed)")
		(string(uprintable_cmd_ext).append(",x").c_str(), "encode unprintable characters as [<char hexadecimal code>] ")
		(string(raw_cmd).append(",r").c_str(), "show raw stream. it is a shortcat for  -l %request%response")
		(string(not_found_string).append(",n").c_str(), po::value<string>()->default_value(default_not_found), string("default \"not found\" value, default is ").append(default_not_found).c_str())
		(string(max_concurrent_tcp_stream).append(",s").c_str(), po::value<int>(&max_concurrent_tcp_stream_v)->default_value(1024), "Max concurrent tcp streams")
		(string(max_fragmented_ip_hosts).append(",d").c_str(), po::value<int>(&max_fragmented_ip_hosts_v)->default_value(1024), "Max concurrent fragmented ip host")
		(string(force_read_pcap).append(",F").c_str(), "force the reading of the pcap file ignoring the snaplen value. WARNING: could give unexpected results")
		(string(capture_in_the_middle).append(",m").c_str(), "capture in the middle. WARNING: could give unexpected results")
		(string(python_function).append(",P").c_str(), po::value<string>(), "execute a python function 'app' in the python given script")
		(string(no_newline).append(",N").c_str(), "no automatic newline at the end of each log");
		po::variables_map vm;
		po::store(po::parse_command_line(argc, argv, desc), vm);

		if (vm.count(help_cmd))
		{
			show_usage(p);
			return 1;
		}
		if (vm.count(version_cmd))
		{
			show_version();
			return 1;
		}

		pos::filtering_stream<pos::output> out;
		if (vm.count(uprintable_cmd_ext) && vm.count(uprintable_cmd))
		{
			print_error("you cannot simultaneously specify ") << uprintable_cmd << " and " << uprintable_cmd_ext << " options\n";
			return -1;
		}

		if (vm.count(uprintable_cmd))
		{
			out.push(ascii_filter());
		}

		if (vm.count(uprintable_cmd_ext))
		{
			out.push(ascii_filter_ext());
		}
		out.push(std::cout);

		po::variable_value config = vm[config_cmd];
		if (!config.empty())
		{
			po::store(po::parse_command_line(argc, argv, desc), vm);
			string filename = config.as<string>();
			ifstream ifs(filename.c_str());
			if (!ifs.is_open())
			{
				print_error("cannot open the specified configuration file '") << filename << "'\n";
				return -1;
			}
			po::store(po::parse_config_file(ifs, desc), vm);
		}
		po::notify(vm);

		// set nids_params
		// check pcap file
		po::variable_value pcapfile_arg = vm[filecap_cmd];
		po::variable_value device_arg = vm[interface_cmd];
		// cannot be be both specified
		if (!pcapfile_arg.empty() && !device_arg.empty())
		{
			print_error("you cannot simultaneously specify capture file and interface\n");
			return -1;
		}
		string pcap_filename;
		if (pcapfile_arg.empty())
			nids_params.filename = NULL;
		else
		{
			pcap_filename = pcapfile_arg.as<string>();
			if (!vm.count(force_read_pcap) && (pcap_filename != "-"))
				check_pcap_file(pcap_filename);
			nids_params.filename = (char *)pcap_filename.c_str();
		}

		if (device_arg.empty())
			nids_params.device = NULL;
		else
			nids_params.device = (char *)device_arg.as<string>().c_str();

		po::variable_value capture_filter_arg = vm[packet_filter_cmd];
		string capture_filter;
		if (capture_filter_arg.empty())
			nids_params.pcap_filter = (char *)default_packet_filter;
		else
		{
			capture_filter = boost::algorithm::join(vm[packet_filter_cmd].as<vector<string>>(), " ");
			nids_params.pcap_filter = (char *)capture_filter.c_str();
		}

		nids_params.scan_num_hosts = 0;
		nids_params.pcap_timeout = 10;
		nids_params.tcp_workarounds = 1;

		// Thanks to Benet Leong
		nids_params.n_tcp_streams = max_concurrent_tcp_stream_v;
		nids_params.n_hosts = max_fragmented_ip_hosts_v;
		// we don want to log intrusions
		nids_params.syslog = reinterpret_cast<void (*)()>(null_syslog);
		bool bcapture_in_the_middle = (vm.count(capture_in_the_middle) > 0) ? true : false;
		nids_params.reassemble_in_the_middle = bcapture_in_the_middle;
		if (!nids_init())
		{
			print_error(nids_errbuf) << "\n";
			return -1;
		}

		po::variable_value python_function_arg = vm[python_function];
		po::variable_value execute_cmd_arg = vm[execute_cmd];
		po::variable_value user_arg = vm[user_cmd];
		printer::ptr _printer;
		if (execute_cmd_arg.empty() && python_function_arg.empty())
		{
			
			_printer = printer::ptr(new outstream_printer(out, vm.count(no_newline) > 0));
		}
		else if (vm.count(execute_cmd))
		{
			if (!user_arg.empty())
				_printer = printer::ptr(new cmd_execute_printer(execute_cmd_arg.as<string>(), user_arg.as<string>()));
			else
				_printer = printer::ptr(new cmd_execute_printer(execute_cmd_arg.as<string>()));
		}
		else if (vm.count(python_function))
		{
			if (!user_arg.empty())
				_printer = printer::ptr(new python_printer(python_function_arg.as<string>(), user_arg.as<string>()));
			else
				_printer = printer::ptr(new python_printer(python_function_arg.as<string>()));
		//cerr.flush();
		}
		p.set_printer(_printer.get());

		p.set_handle_truncated(vm.count(handle_truncated_cmd));
		p.set_default_not_found(vm[not_found_string].as<string>());
		// parse output format specifications
		po::variable_value raw_arg = vm[raw_cmd];
		po::variable_value logformat_arg = vm[logformat_cmd];
		po::variable_value append_logformat_arg = vm[append_logformat_cmd];
		vector<string> args;
		args.push_back(raw_cmd);
		args.push_back(logformat_cmd);
		args.push_back(append_logformat_cmd);
		if (check_conflicts(vm, args))
			return -1;

		if (vm.count(append_logformat_cmd))
			p.parse(string(default_format).append(append_logformat_arg.as<string>()).c_str());
		else if (vm.count(raw_cmd))
			p.parse(raw_format);
		else
		{
			if (vm.count(logformat_cmd))
			{
				auto s = boost::algorithm::join(logformat_arg.as<vector<string>>(), " ");
				p.parse(s.c_str());
			}
			else
				p.parse(default_format);
		}
		union
		{
			void (*func)(struct tcp_stream *ts, void **yoda, struct timeval *t, unsigned char *packet);
			void *ptr_nids_handler;

		} un;
		un.func = parser::nids_handler;

		nids_register_tcp(un.ptr_nids_handler);

		// avoid checksum , sometime libnids fails, so
		// we trust in kernel checks that let the streaming flow to continue.
		nids_chksum_ctl chksumctl[1];
		chksumctl[0].netaddr = ip_to_ulong(0, 0, 0, 0);
		chksumctl[0].mask = ip_to_ulong(0, 0, 0, 0);
		chksumctl[0].action = NIDS_DONT_CHKSUM;

		nids_register_chksum_ctl(chksumctl, 1);
		signal_thread  = boost::thread(&run_signal_service);
		nids_run();
		parser::theOnlyParser->process_truncated();
		io_service.stop();
		signal_thread.join();
		// reached when parsing file
		exit(0);
	}
	catch (po::error &e)
	{
		print_error(e.what()) << "\n\n";
		show_usage(p);
		return -1;
	}
	catch (exception &e)
	{
		print_error(e.what()) << "\n";
		return -1;
	}
	catch (...)
	{
		print_error("Exception of unknown type!\n");
		return -1;
	}
}
void show_usage(parser &p)
{
	cout << desc << "\n"
		 << "FORMAT KEYWORDS:\n";
	for (parser::parse_elements::iterator it = p.keywords_begin(); it != p.keywords_end(); it++)
	{
		cout << "\t" << parser::_key_word_id << (*it).first << "\n";
	}
}
