/*
	Copyright (c) 2007 Plecno s.r.l. All Rights Reserved 
	info@plecno.com
	via Giovio 8, 20144 Milano, Italy

	Released under the terms of the GPLv3 or later

	Author: Oreste Notelli <oreste.notelli@plecno.com>	
*/

#include "regex.h"

using namespace std;

string regex(const boost::regex& re, const string& text)
{
	string result;
	boost::smatch what;
	if (boost::regex_search(text, what, re))
	for (boost::smatch::const_iterator it = what.begin(); it != what.end(); it++)
	{
		result.assign(*it);
	}
	return result;
}

void regex_handler_base::append(std::basic_ostream<char>& out, const timeval*,connections_container* pconnections_container)
{
	string res = ::regex(_re, get_text());
	if (res.empty())
		out << _not_found;
	else
		out<<res;
}



#include <string>
#include <cstdint>

#define _MIN_SNI_SIZE 5
#define _MAX_SNI_SIZE 255

std::string extract_sni_from_string(const std::string& data) {
    size_t len = data.size();
    if (len < 5)
        return "";

    // Search for a TLS handshake record start to tolerate leading bytes.
    size_t pos = 0;
    for (; pos + 5 <= len; ++pos) {
        if ((uint8_t)data[pos] == 0x16 && (uint8_t)data[pos + 1] == 0x03)
            break;
    }
    if (pos + 5 > len)
        return "";

    // Skip TLS record header.
    pos += 5;
    if (pos + 4 > len) return "";
    if ((uint8_t)data[pos] != 0x01) return "";
    pos += 4;
    if (pos + 34 > len) return "";
    pos += 34;
    if (pos >= len) return "";
    uint8_t session_id_len = (uint8_t)data[pos];
    pos += 1 + session_id_len;
    if (pos + 2 > len) return "";
    uint16_t cipher_suites_len = ((uint8_t)data[pos] << 8) | (uint8_t)data[pos+1];
    pos += 2 + cipher_suites_len;
    if (pos + 1 > len) return "";
    uint8_t comp_methods_len = (uint8_t)data[pos];
    pos += 1 + comp_methods_len;
    if (pos + 2 > len) return "";
    uint16_t ext_len = ((uint8_t)data[pos] << 8) | (uint8_t)data[pos+1];
    pos += 2;
    size_t ext_end = pos + ext_len;
    while (pos + 4 <= ext_end && pos + 4 <= len) {
        uint16_t ext_type = ((uint8_t)data[pos] << 8) | (uint8_t)data[pos+1];
        uint16_t ext_size = ((uint8_t)data[pos+2] << 8) | (uint8_t)data[pos+3];
        pos += 4;
        if (ext_type == 0x00 && ext_size >= 5) { // SNI
            size_t sni_ext_end = pos + ext_size;
            if (pos + 2 > sni_ext_end || pos + 2 > len) return "";
            uint16_t sni_list_len = ((uint8_t)data[pos] << 8) | (uint8_t)data[pos+1];
            size_t sni_list_pos = pos + 2;
            size_t sni_list_end = sni_list_pos + sni_list_len;
            if (sni_list_end > sni_ext_end)
                sni_list_end = sni_ext_end;

            while (sni_list_pos + 3 <= sni_list_end && sni_list_pos + 3 <= len) {
                uint8_t sni_type = (uint8_t)data[sni_list_pos];
                uint16_t sni_name_len = ((uint8_t)data[sni_list_pos+1] << 8) | (uint8_t)data[sni_list_pos+2];
                sni_list_pos += 3;
                if (sni_type == 0x00 && sni_list_pos + sni_name_len <= sni_list_end && sni_list_pos + sni_name_len <= len) {
                    return data.substr(sni_list_pos, sni_name_len);
                }
                sni_list_pos += sni_name_len;
            }
            break;
        }
        pos += ext_size;
    }
    return "";
}

void sni_extractor::onRequest(tcp_stream *pstream, const timeval *t)
{
    if (content.size() < _MAX_SNI_SIZE)
        content.append(pstream->server.data, pstream->server.data + pstream->server.count_new);
    
}

void sni_extractor::append(std::basic_ostream<char>& out, const timeval*, connections_container*) {
    sni = extract_sni_from_string(content);
    if (sni.empty())
        out << _not_found;
    else    
        out << sni;
}

string& sni_extractor::get_text() {
	return sni;
}

