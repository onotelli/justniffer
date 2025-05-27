import struct
from dataclasses import dataclass
from typing import Any
from justniffer.logging import logger
from os import listdir


def parse_ssh_banner(data: bytes) -> tuple[str, bytes] | None:
    endline = b'\r\n'
    if data.find(endline) > 0:
        banner, rest = data.split(endline, 1)
        try:
            banner_str = banner.decode('ascii')
            return banner_str, rest
        except UnicodeDecodeError:
            return None
    return None


def parse_ssh_packet(packet: bytes) -> tuple[bytes, int, int] | None:
    if len(packet) < 5:
        return None
    packet_length = int.from_bytes(packet[0:4], byteorder='big')
    padding_length = packet[4]
    payload_length = packet_length - padding_length - 1
    payload = packet[5:5+payload_length]
    return payload, packet_length, padding_length


def parse_string_field(data: bytes, offset: int) -> tuple[str, int] | None:
    if offset + 4 > len(data):
        logger.warning('parse_string_field: Not enough data for length field.')
        return None
    length = struct.unpack('>I', data[offset:offset+4])[0]
    current_offset_after_length_field = offset + 4

    if current_offset_after_length_field + length > len(data):
        logger.warning(f'parse_string_field: Declared string length ({length}) exceeds available data ({len(data) - current_offset_after_length_field}).')
        return None

    field_bytes = data[current_offset_after_length_field: current_offset_after_length_field + length]
    new_offset = current_offset_after_length_field + length

    return field_bytes.decode('ascii', errors='replace'), new_offset


FIELD_NAMES = [
    'kex_algorithms',
    'server_host_key_algorithms',
    'encryption_algorithms_client_to_server',
    'encryption_algorithms_server_to_client',
    'mac_algorithms_client_to_server',
    'mac_algorithms_server_to_client',
    'compression_algorithms_client_to_server',
    'compression_algorithms_server_to_client',
    'languages_client_to_server',
    'languages_server_to_client'
]


@dataclass
class KexInitInfo:
    msg_type: int
    cookie: str
    fields: dict
    first_kex_packet_follows: bool
    reserved: int


@dataclass
class SSHInfo:
    client_banner: str
    server_banner: str
    kexinit: KexInitInfo | None


def parse_kexinit_payload(payload: bytes) -> KexInitInfo | None:
    offset = 0
    if not payload:  # Handle empty payload case
        logger.warning('parse_kexinit_payload: Received empty payload.')
        return None

    msg_type = payload[offset]
    offset += 1
    if msg_type != 20:  # SSH_MSG_KEXINIT must be 20.
        logger.warning(f'parse_kexinit_payload: Incorrect message type {msg_type}, expected 20.')
        return None

    # Cookie: 16 bytes
    if offset + 16 > len(payload):
        logger.warning('parse_kexinit_payload: Not enough data for cookie.')
        return None
    cookie = payload[offset:offset+16]
    offset += 16

    fields = {}
    for name in FIELD_NAMES:
        field_res = parse_string_field(payload, offset)
        if field_res is None:  # Check if parsing the string field failed
            logger.warning(f'parse_kexinit_payload: Failed to parse string field "{name}".')
            return None  # Abort parsing if a field is malformed
        value, offset = field_res
        fields[name] = value

    # first_kex_packet_follows (boolean)
    if offset >= len(payload):
        logger.warning('parse_kexinit_payload: Not enough data for "first_kex_packet_follows".')
        return None
    first_kex_packet_follows = bool(payload[offset])
    offset += 1

    # reserved (uint32)
    if offset + 4 > len(payload):
        logger.warning('parse_kexinit_payload: Not enough data for "reserved" field.')
        return None
    reserved = int.from_bytes(payload[offset:offset+4], 'big')
    # offset += 4 # This offset update is not strictly needed if it's the last field

    return KexInitInfo(
        msg_type=msg_type,
        cookie=cookie.hex(),
        fields=fields,
        first_kex_packet_follows=first_kex_packet_follows,
        reserved=reserved
    )


# Example response as provided:
response = (
    b'SSH-2.0-OpenSSH_8.9p1\r\n'
    b'\x00\x00\x04T'  # packet_length = 0x00000454 = 1108 bytes (for the rest of the packet)
    b'\n'            # padding_length = 10 (0x0A in decimal)
    b'\x14'          # SSH_MSG_KEXINIT (20 decimal)
    b'l\xe0\x05\xe9\xbeW=B\x80%>e\xcd\xbd\xaa\x05'  # 16-byte cookie
    b'\x00\x00\x01&'
    b'curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,'
    b'ecdh-sha2-nistp521,sntrup761x25519-sha512@openssh.com,diffie-hellman-group-exchange-sha256,'
    b'diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,'
    b'kex-strict-s-v00@openssh.com'
    b'\x00\x00\x00\x39'
    b'rsa-sha2-512,rsa-sha2-256,ecdsa-sha2-nistp256,ssh-ed25519'
    b'\x00\x00\x00l'
    b'chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,'
    b'aes128-gcm@openssh.com,aes256-gcm@openssh.com'
    b'\x00\x00\x00l'
    b'chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,'
    b'aes128-gcm@openssh.com,aes256-gcm@openssh.com'
    b'\x00\x00\x00\xd5'
    b'umac-64-etm@openssh.com,umac-128-etm@openssh.com,'
    b'hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,'
    b'hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,'
    b'hmac-sha2-256,hmac-sha2-512,hmac-sha1'
    b'\x00\x00\x00\xd5'
    b'umac-64-etm@openssh.com,umac-128-etm@openssh.com,'
    b'hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,'
    b'hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,'
    b'hmac-sha2-256,hmac-sha2-512,hmac-sha1'
    b'\x00\x00\x00\x15'
    b'none,zlib@openssh.com'
    b'\x00\x00\x00\x15'
    b'none,zlib@openssh.com'
    b'\x00\x00\x00\x00'  # languages_client_to_server (empty)
    b'\x00\x00\x00\x00'  # languages_server_to_client (empty)
    b'\x00'            # first_kex_packet_follows (false)
    b'\x00\x00\x00\x00'  # reserved (uint32, 0)
)

def extract_kexinit_info(payload: bytes) -> KexInitInfo | None:
    kexinit_res = parse_ssh_packet(payload)
    kexinit = None
    if kexinit_res is not None:
        subpayload, pkt_length, pad_length = kexinit_res
        kexinit = parse_kexinit_payload(subpayload)
    return kexinit

def ssh_info(request: bytes, response: bytes) -> SSHInfo | None:
    client_banner_res = parse_ssh_banner(request)
    client_banner = None
    if client_banner_res is None:
        return None
    client_banner = client_banner_res[0]
    banner_res = parse_ssh_banner(response)
    if banner_res is None:
        return None
    banner, remaining = banner_res
    return SSHInfo(
        client_banner=client_banner,
        server_banner=banner,
        kexinit=extract_kexinit_info(remaining)
    )


def test() -> None:
    def _(*args: Any) -> str:
        return ' '.join([str(a) for a in args])

    tmp_dir = '/tmp/ssh'
    for fname in listdir(tmp_dir):
        # if '-1-' in fname:
        if True:
            logger.debug(_(f'File: {fname}'))
            with open(f'{tmp_dir}/{fname}', 'rb') as f:
                request = f.read()
                banner_res = parse_ssh_banner(request)
                if banner_res is None:
                    continue
                banner, remaining = banner_res
                logger.debug(_('Banner:', banner))
                res = parse_ssh_packet(remaining)
                if res is not None:
                    payload, pkt_length, pad_length = res
                    logger.debug(_('Packet Length:', pkt_length))
                    logger.debug(_('Padding Length:', pad_length))
                    kexinit = parse_kexinit_payload(payload)
                    if kexinit is not None:
                        logger.debug(_('\n--- Parsed SSH_MSG_KEXINIT Fields ---'))
                        logger.debug(_('Message Type:', kexinit.msg_type))  # Should be 20 for SSH_MSG_KEXINIT
                        logger.debug(_('Cookie:', kexinit.cookie))
                        for field_name, value in kexinit.fields.items():
                            logger.debug(_(f'{field_name}: {value}'))
                        logger.debug(_('First KEX Packet Follows:', kexinit.first_kex_packet_follows))
                        logger.debug(_('Reserved (should be 0):', kexinit.reserved))
