import sys
import os

# Path to the target environment's site-packages
target_env_path = '/opt/midesa/projects/justniffer/tmp/env/test/lib64/python3.10/site-packages/'

# Add the target environment's site-packages to the beginning of sys.path
sys.path.insert(0, target_env_path)

# Now imports will prioritize the target environment's libraries



from scapy.layers.tls.all import TLS
from scapy.layers.tls.handshake import TLSClientHello, TLSServerHello, TLSCertificate
from  scapy.layers.tls.crypto import suites

from loguru import logger
import ssl


_codes = dict()

for c in suites.__dict__.values():
    try:
        _codes[c.val]= c.name
    except:
        pass


context = ssl.create_default_context()
ciphers = context.get_ciphers()

chipher_names = dict([(cipher['id'], cipher['name']) for cipher in ciphers])

REQUEST_DELIMITER =b'------- REQUEST --------\n'
RESPONSE_DELIMITER =b'\n----------  RESPONSE  -----------\n'


def print_tls_info(tls_packet: TLS):
    """Print useful TLS information from a Scapy TLS packet."""
    logger.info('print_tls')
    if not tls_packet:
        print("No TLS data found.")
        return
    # Iterate through TLS layers
    while tls_packet:
        # Check for TLS Record Layer
        if isinstance(tls_packet, TLS):

            # Check if this is a Handshake message
            if tls_packet.type == 22:  # 22 = Handshake
                handshake = tls_packet.msg[0] # type: ignore
                if isinstance(handshake, TLSClientHello):
                    print("\n[ClientHello]")
                    print(f"  TLS Version: {handshake.version}")
                    ciphers = [
                        _cipher_name(c) 
                        for c in handshake.ciphers or []
                    ]

                    print(f"  Cipher Suites: {ciphers}")
                    # Extract SNI (Server Name Indication) if present
                    for ext in handshake.ext: # type: ignore
                        if ext.type == 0x00:  # SNI extension
                            sni = ext.servernames[0].servername.decode()
                            print(f"  SNI: {sni}")
                elif isinstance(handshake, TLSServerHello):
                    print("\n[ServerHello]")
                    print(f"  TLS Version: {handshake.version}")
                    print(f"  Selected Cipher Suite: {_cipher_name(handshake.cipher)}")# type: ignore
                elif isinstance(handshake, TLSCertificate):
                    print("\n[Certificate]")
                    print(f"  Certificates: {len(handshake.certs)} presented")# type: ignore

            elif tls_packet.type == 23:  # Application Data
                print("\n[Application Data] (Encrypted)")

            elif tls_packet.type == 21:  # Alert
                print("\n[Alert]")
                print(f"  Level: {tls_packet.level}")
                print(f"  Description: {tls_packet.description}")

        # Move to the next layer
        tls_packet = tls_packet.payload 

def _cipher_name(c: int) -> str:
    return _codes.get(c,  f"Unknown (0x{c:04x})")# type: ignore

def print_tls(tls_packet) -> None:    
    print_tls_info(tls_packet)



def read_content():
    with open('content', 'rb') as file_:
        c = file_.read()
        start_pos = 0
        while True:
            req_pos = c.find(REQUEST_DELIMITER, start_pos)
            if req_pos == -1:
                break  # No more request delimiters found
            start_request = req_pos + len(REQUEST_DELIMITER)
            res_pos = c.find(RESPONSE_DELIMITER, start_request)
            if res_pos == -1:
                break  # No matching response delimiter found
            request = c[start_request:res_pos]
            resp_start = res_pos + len(RESPONSE_DELIMITER)
            next_req_pos = c.find(REQUEST_DELIMITER, resp_start)
            if next_req_pos == -1:
                logger.info('Last request-response pair')
                response = c[resp_start:]
                # Process last response
                req = TLS(request)
                resp = TLS(response)

                print_tls(req)
                print_tls(resp)
                break
            else:
                logger.info('Request-response pair')
                response = c[resp_start:next_req_pos]
                # Process request-response pair
                req = TLS(request)
                resp = TLS(response)
                print_tls(req)
                print_tls(resp)
                start_pos = next_req_pos
        

if __name__ == '__main__':
    read_content()        


# file_ = open('content')
# c = file_.read()
# file_ = open('content', 'rb')
# c = file_.read()
# c.find('\n')
# c.find(b'\n')
# c.find(b'----\n')
# c.find(20, b'----\n')
# c.find?
# c.find(b'----\n', 21)
# c.find(b'----\n')
# c.find(b'----\n', 20)
# c.find(b'----\n', 21)
# c[20:572]
# c.find(b'\n----------   RESPO', 20)
# c.find(b'\n----------  RESPO', 20)
# c[20:542]
# c[20+len(b'----\n'):542]
# brequest = c[20+len(b'----\n'):542]
# from scapy.layers.tls import TLS
# from scapy.layers.tls.all import TLS
# tls = TLS(brequest)
# tls
# tls.type
# tls.raw_packet_cache
# tls.padlen
# tls.direction
# tls.msg
# tls.msg[0]
# len (tls.msg)
# msg = tls.msg
# msg = tls.msg[0]
# msg.ciphers
# msg.process_information
# msg.fields
# msg.ext
# msg.ext[0]
# len(msg.ext)
# extname = msg.ext[0]

# extname.servernames
# extname.servernames[0]
# extname.servernames[0].servername
# extname.servernames[0].servername.decode()
# c
# c.splitlines()
# c.find(b'----------  RESPONSE  -----------')
# c.find(b'----------  RESPONSE  -----------\n')
# len(b'----------  RESPONSE  -----------\n')
# c[ c.find(b'----------  RESPONSE  -----------\n')+len(b'----------  RESPONSE  -----------\n'):]
# c[ c.find(b'----------  RESPONSE  -----------\n')+len(b'----------  RESPONSE  -----------\n'):][:200]
# c[ c.find(b'----------  RESPONSE  -----------\n')+len(b'----------  RESPONSE  -----------\n')-1:][:200]
# c[ c.find(b'----------  RESPONSE  -----------\n')+len(b'----------  RESPONSE  -----------\n'):][:200]
