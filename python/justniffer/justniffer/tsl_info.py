from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, cast, Type
from scapy.layers.tls.all import TLS
from scapy.layers.tls.handshake import TLSClientHello, TLSServerHello
from scapy.layers.tls.record import TLSChangeCipherSpec
from scapy.layers.tls.crypto import suites
import ssl
from justniffer.logging import logger

context = ssl.create_default_context()
ciphers = context.get_ciphers()

chipher_names = dict([(cipher['id'], cipher['name']) for cipher in ciphers])

_codes = dict()

for c in suites.__dict__.values():
    try:
        _codes[c.val] = c.name
    except:
        pass


def _cipher_name(c: int | None) -> str:
    return _codes.get(c,  f'Unknown (0x{c:04x})')  # type: ignore


class TLSVersion(Enum):
    TLS_1_3 = 772
    TLS_1_2 = 771
    TLS_1_1 = 770
    TLS_1_0 = 769
    SSL_3_0 = 768

    @classmethod
    def from_int(cls, value: int | None):
        try:
            if value is None:
                return None
            else:
                return cls(value)
        except ValueError:
            return None


def _get_TLS_VERSION(n: Any) -> TLSVersion | None:
    if n is None:
        return None
    res = TLSVersion.from_int(n)
    if res is None:
        logger.warning(f'TSL VERSION not found {n=} ')
    return res


@dataclass
class Msg:
    name: str


@dataclass
class ClientHelloMsg(Msg):
    sid: bytes | None
    sni_list: list[str]
    ciphers: list[str]
    versions: list[TLSVersion | None]


@dataclass
class ServerHelloMsg(Msg):
    sid: bytes
    cipher: str
    version: TLSVersion | None


@dataclass
class TLSContent:
    name: str


class TlsContentType(IntEnum):
    CHANGE_CIPHER_SPEC = 20
    ALERT = 21
    HANDSHAKE = 22
    APPLICATION_DATA = 23
    HEARTBEAT = 24
    TLS12_CID = 25
    ACK = 26

    def __str__(self):
        return self.name

    @classmethod
    def from_int(cls, value: int | None):
        try:
            if value is None:
                return None
            else:
                return cls(value)
        except ValueError:
            return None


@dataclass
class TLSInfo(TLSContent):
    type: TlsContentType | None
    msgs: list[Msg]
    version: TLSVersion | None


def remove_key_share_extension_clienthello(raw_bytes: bytes) -> bytes:
    fixed_offset = 38
    session_id_length = raw_bytes[fixed_offset]
    session_id_end = fixed_offset + 1 + session_id_length
    cipher_suites_len = int.from_bytes(raw_bytes[session_id_end:session_id_end+2], byteorder='big')
    cipher_suites_end = session_id_end + 2 + cipher_suites_len
    comp_offset = cipher_suites_end
    compression_methods_len = raw_bytes[comp_offset]
    compression_methods_end = comp_offset + 1 + compression_methods_len
    ext_length_offset = compression_methods_end
    ext_block_length = int.from_bytes(raw_bytes[ext_length_offset:ext_length_offset+2], byteorder='big')
    ext_block_start = ext_length_offset + 2
    ext_block_end = ext_block_start + ext_block_length
    ext_block = raw_bytes[ext_block_start:ext_block_end]
    new_exts = b""
    i = 0
    while i < len(ext_block):
        ext_type = ext_block[i:i+2]
        ext_len = int.from_bytes(ext_block[i+2:i+4], byteorder='big')
        ext_data = ext_block[i+4:i+4+ext_len]
        if ext_type != b"\x00\x33":
            new_exts += ext_type + ext_block[i+2:i+4] + ext_data
        else:
            logger.debug('Removing Key Share extension from ClientHello')
        i += 4 + ext_len
    new_ext_len_bytes = len(new_exts).to_bytes(2, byteorder='big')
    new_raw = (
        raw_bytes[:ext_length_offset] +
        new_ext_len_bytes +
        new_exts +
        raw_bytes[ext_block_end:]
    )
    return new_raw


def _remove_key_share_extension(raw_bytes: bytes) -> bytes:
    handshake_type = raw_bytes[0]
    if handshake_type == 0x01:
        offset = 1 + 3 + 2 + 32
        session_id_length = raw_bytes[offset]
        offset += 1 + session_id_length
        cipher_suites_length = int.from_bytes(raw_bytes[offset:offset+2], byteorder='big')
        offset += 2 + cipher_suites_length
        compression_length = raw_bytes[offset]
        offset += 1 + compression_length
        ext_length_offset = offset
    elif handshake_type == 0x02:
        offset = 1 + 3 + 2 + 32
        session_id_length = raw_bytes[offset]
        offset += 1 + session_id_length
        offset += 2 + 1
        ext_length_offset = offset
    else:
        logger.debug(f'Unknown handshake type (0x{handshake_type:02x}). Returning raw bytes unchanged')
        return raw_bytes
    ext_block_length = int.from_bytes(raw_bytes[ext_length_offset:ext_length_offset+2], byteorder='big')
    ext_block_start = ext_length_offset + 2
    ext_block_end = ext_block_start + ext_block_length
    ext_block = raw_bytes[ext_block_start:ext_block_end]
    new_exts = b""
    pos = 0
    while pos < len(ext_block):
        ext_type = ext_block[pos: pos+2]
        ext_len = int.from_bytes(ext_block[pos+2: pos+4], byteorder='big')
        ext_data = ext_block[pos+4: pos+4+ext_len]
        if ext_type != b'\x00\x33':
            new_exts += ext_type + ext_block[pos+2: pos+4] + ext_data
        else:
            logger.debug('Removing Key Share extension (type 0x0033)')
        pos += 4 + ext_len
    new_ext_len_bytes = len(new_exts).to_bytes(2, byteorder='big')
    new_raw = raw_bytes[:ext_length_offset] + new_ext_len_bytes + new_exts + raw_bytes[ext_block_end:]
    return new_raw


def _identify_tls_message_type(raw_bytes: bytes) -> Type[TLSClientHello | TLSServerHello] | None:
    handshake_type = raw_bytes[0]
    if handshake_type == 0x01:
        return TLSClientHello
    elif handshake_type == 0x02:
        return TLSServerHello
    else:
        return None


def get_TLSInfo(content: bytes) -> TLSContent | None:
    tls_packet = TLS(content)
    name = tls_packet.__class__.__name__

    if isinstance(tls_packet, TLS):
        msgs: list[Msg] = []
        version = _get_TLS_VERSION(getattr(tls_packet, 'version', None))
        for msg in tls_packet.msg or []:
            msg_name = msg.__class__.__name__
            if isinstance(msg, TLSClientHello):
                versions = []
                sni_list: list[str] = []
                ciphers = [
                    _cipher_name(c)
                    for c in msg.ciphers or []
                ]
                for ext in msg.ext:  # type: ignore
                    if ext.type == 0x00:  # SNI extension
                        for sn in ext.servernames:
                            sni = sn.servername.decode()
                            sni_list.append(sni)
                    elif ext.type == 0x2b:
                        versions = [_get_TLS_VERSION(v) for v in ext.versions]

                msgs.append(ClientHelloMsg(msg_name, cast(bytes, msg.sid), ciphers=ciphers, sni_list=sni_list, versions=versions))
            elif isinstance(msg, TLSServerHello):
                version, cipher = _get_version_cipher(msg)
                msgs.append(ServerHelloMsg(msg_name, cast(bytes, msg.sid), cipher, version=version))
            elif msg.name == 'Raw':
                msg_class = _identify_tls_message_type(msg.load)
                if msg_class is None:
                    msgs.append(Msg(msg_name))
                else:
                    msg_ = msg_class(_remove_key_share_extension(msg.load))
                    version, cipher = _get_version_cipher(msg_)  # type: ignore
                    msg_name = msg_.__class__.__name__
                    msgs.append(ServerHelloMsg(msg_name, cast(bytes, msg_.sid), cipher, version=version))
            else:
                msgs.append(Msg(msg_name))
        return TLSInfo(name, TlsContentType.from_int(cast(int,  getattr(tls_packet, 'type', None))), msgs, version)
    elif 'TLS' in tls_packet.__class__.__name__:
        return TLSContent(name)
    else:
        return None


def _get_version_cipher(msg: TLSServerHello) -> tuple[TLSVersion | None, str]:
    version = None
    cipher = _cipher_name(msg.cipher)
    for ext in msg.ext or []:
        if ext.type == 0x2b:
            version = _get_TLS_VERSION(ext.version)
    if version is None:
        version = _get_TLS_VERSION(msg.version)
    return version, cipher
