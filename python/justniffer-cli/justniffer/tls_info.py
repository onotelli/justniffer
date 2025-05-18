import ssl
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, cast
from datetime import datetime
from time import mktime

from justniffer.model import TLSVersion
from scapy.packet import Packet, Raw
from scapy.layers.tls.all import TLS
from scapy.layers.tls.handshake import (
    TLSClientHello,
    TLSServerHello,
    TLSCertificate
)
from scapy.layers.tls.record import TLSChangeCipherSpec
from scapy.layers.tls.crypto import suites as scapy_suites

from justniffer.logging import logger


def _remove_key_share_extension(raw_bytes: bytes) -> bytes:
    ''' 
        to resolve parsing limitations in Scapy version 2.6.1 when handling the Key Share extension
    '''
    if not raw_bytes:
        return raw_bytes

    try:
        handshake_type = raw_bytes[0]
        base_offset = 1 + 3 + 2 + 32
        offset = base_offset

        if handshake_type == TlsHandshakeType.CLIENT_HELLO:
            if len(raw_bytes) <= offset:
                return raw_bytes
            session_id_length = raw_bytes[offset]
            offset += 1 + session_id_length
            if len(raw_bytes) < offset + 2:
                return raw_bytes
            cipher_suites_length = int.from_bytes(raw_bytes[offset:offset+2], byteorder='big')
            offset += 2 + cipher_suites_length
            if len(raw_bytes) <= offset:
                return raw_bytes
            compression_length = raw_bytes[offset]
            offset += 1 + compression_length
            ext_length_offset = offset
        elif handshake_type == TlsHandshakeType.SERVER_HELLO:
            if len(raw_bytes) <= offset:
                return raw_bytes
            session_id_length = raw_bytes[offset]
            offset += 1 + session_id_length
            if len(raw_bytes) < offset + 2:
                return raw_bytes
            offset += 2
            if len(raw_bytes) <= offset:
                return raw_bytes
            offset += 1
            ext_length_offset = offset
        else:
            logger.debug(f'handshake type (0x{handshake_type:02x}) not client/server hello, not removing key share.')
            return raw_bytes

        if len(raw_bytes) < ext_length_offset + 2:
            return raw_bytes

        ext_block_length = int.from_bytes(raw_bytes[ext_length_offset:ext_length_offset+2], byteorder='big')
        ext_block_start = ext_length_offset + 2
        ext_block_end = ext_block_start + ext_block_length

        if ext_block_end > len(raw_bytes):
            logger.warning('malformed extensions block: length exceeds available bytes. returning original bytes')
            return raw_bytes
        if ext_block_length == 0:
            return raw_bytes

        ext_block = raw_bytes[ext_block_start:ext_block_end]
        new_exts = b''
        pos = 0
        key_share_removed = False
        while pos < len(ext_block):
            if pos + 4 > len(ext_block):
                logger.warning('malformed extension entry (too short for header) near end of block. stopping parse')
                return raw_bytes

            ext_type_bytes = ext_block[pos: pos+2]
            ext_len = int.from_bytes(ext_block[pos+2: pos+4], byteorder='big')
            ext_data_start = pos + 4
            ext_data_end = ext_data_start + ext_len

            if ext_data_end > len(ext_block):
                logger.warning(f'malformed extension entry (type 0x{ext_type_bytes.hex()}): '
                               f'length {ext_len} exceeds remaining block size {len(ext_block) - ext_data_start} '
                               'stopping parse')
                return raw_bytes

            if ext_type_bytes == TlsExtensionType.KEY_SHARE.to_bytes(2, 'big'):
                logger.debug('removing key share extension (type 0x0033)')
                key_share_removed = True
            else:
                new_exts += ext_block[pos: ext_data_end]

            pos = ext_data_end

        if not key_share_removed:
            return raw_bytes

        new_ext_len_bytes = len(new_exts).to_bytes(2, byteorder='big')
        remaining_bytes_after_ext = raw_bytes[ext_block_end:]

        new_raw_handshake = (
            raw_bytes[:ext_length_offset] +
            new_ext_len_bytes +
            new_exts +
            remaining_bytes_after_ext
        )

        logger.debug(f'removed key share, original ext block len={ext_block_length}, '
                     f'new ext block len={len(new_exts)}. '
                     f'original total len={len(raw_bytes)}, new approx len={len(new_raw_handshake)}')
        return new_raw_handshake

    except IndexError:
        logger.warning('indexerror during key share removal, likely malformed packet structure. returning original bytes')
        return raw_bytes
    except Exception as e:
        logger.error(f'unexpected error during key share removal: {e}. returning original bytes', exc_info=True)
        return raw_bytes


class TlsHandshakeType(IntEnum):
    CLIENT_HELLO = 0x01
    SERVER_HELLO = 0x02
    UNKNOWN = -1

    @classmethod
    def from_byte(cls, value: int) -> 'TlsHandshakeType':
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class TlsExtensionType(IntEnum):
    SERVER_NAME = 0x00
    SUPPORTED_VERSIONS = 0x2b
    KEY_SHARE = 0x33


class TlsContentType(IntEnum):
    CHANGE_CIPHER_SPEC = 20
    ALERT = 21
    HANDSHAKE = 22
    APPLICATION_DATA = 23
    HEARTBEAT = 24
    TLS12_CID = 25
    ACK = 26

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_int(cls, value: int | None) -> 'TlsContentType | None':
        if value is None:
            return None
        try:
            return cls(value)
        except ValueError:
            logger.warning(f'unknown tls content type: {value}')
            return None


_CIPHER_SUITE_MAP: dict[int, str] = {}


def _init_cipher_maps():
    global _CIPHER_SUITE_MAP
    if _CIPHER_SUITE_MAP:
        return

    for name, suite in scapy_suites.__dict__.items():
        if hasattr(suite, 'val') and isinstance(suite.val, int):
            _CIPHER_SUITE_MAP[suite.val] = getattr(suite, 'name', name)

    try:
        context = ssl.create_default_context()
        standard_ciphers = context.get_ciphers()
        for cipher in standard_ciphers:
            pass
    except Exception as e:
        logger.warning(f'could not get standard cipher list from ssl module: {e}')

    logger.debug(f'initialized cipher suite map with {len(_CIPHER_SUITE_MAP)} entries')


_init_cipher_maps()


def _get_cipher_name(code: int | None) -> str:
    if code is None:
        return 'unknown (no cipher)'
    return _CIPHER_SUITE_MAP.get(code, f'unknown (0x{code:04x})')


def _parse_tls_version(version_code: int | None) -> TLSVersion | None:
    res = TLSVersion.from_int(version_code)
    return res


@dataclass
class BaseTlsMessageInfo:
    name: str


@dataclass
class ClientHelloInfo(BaseTlsMessageInfo):
    sid: bytes | None
    ciphers: list[str] = field(default_factory=list)
    sni_hostnames: list[str] = field(default_factory=list)
    versions: list[TLSVersion | None] = field(default_factory=list)


@dataclass
class Certificate:
    common_name: str
    organization_name: str
    expires: datetime


@dataclass
class ServerHelloInfo(BaseTlsMessageInfo):
    sid: bytes | None
    cipher: str
    version: TLSVersion | None
    certificate: Certificate | None


@dataclass
class GenericTlsMessageInfo(BaseTlsMessageInfo):
    pass


@dataclass
class TlsRecordInfo:
    name: str
    type: TlsContentType | None
    version: TLSVersion | None
    messages: list[ClientHelloInfo | ServerHelloInfo | GenericTlsMessageInfo] = field(default_factory=list)


def _extract_extensions(msg: Packet) -> dict[int, Any]:
    extensions = {}
    if hasattr(msg, 'ext') and msg.ext is not None:
        for ext in msg.ext:
            if hasattr(ext, 'type') and not isinstance(ext, Raw):
                extensions[ext.type] = ext
            elif isinstance(ext, Raw):
                logger.warning(f'encountered raw extension data: {ext.load!r}')
    return extensions


def _parse_client_hello(msg: TLSClientHello) -> ClientHelloInfo:
    extensions = _extract_extensions(msg)

    sni_hostnames: list[str] = []
    sni_ext = extensions.get(TlsExtensionType.SERVER_NAME)
    if sni_ext and hasattr(sni_ext, 'servernames'):
        for sn in sni_ext.servernames:
            try:
                servername_bytes = sn.servername
                sni_hostnames.append(servername_bytes.decode('utf-8', errors='replace'))
            except Exception as e:
                logger.warning(f'could not decode sni servername: {sn.servername!r} ({e})')
                sni_hostnames.append(f'<{len(sn.servername)} undecoded bytes>')

    supported_versions: list[TLSVersion | None] = []
    versions_ext = extensions.get(TlsExtensionType.SUPPORTED_VERSIONS)
    if versions_ext and hasattr(versions_ext, 'versions'):
        supported_versions = [_parse_tls_version(v) for v in versions_ext.versions]
        if None in supported_versions:
            logger.warning(f'could not parse all supported versions from {versions_ext!r}')

    cipher_suites = [_get_cipher_name(c) for c in msg.ciphers or []]

    return ClientHelloInfo(
        name=msg.__class__.__name__,
        sid=getattr(msg, 'sid', None),
        ciphers=cipher_suites,
        sni_hostnames=sni_hostnames,
        versions=supported_versions
    )


def _parse_server_hello(tls_packet: TLS, msg: TLSServerHello) -> ServerHelloInfo:
    extensions = _extract_extensions(msg)
    selected_version: TLSVersion | None = None

    versions_ext = extensions.get(TlsExtensionType.SUPPORTED_VERSIONS)
    if versions_ext and hasattr(versions_ext, 'version'):
        selected_version = _parse_tls_version(versions_ext.version)

    if selected_version is None:
        selected_version = _parse_tls_version(getattr(msg, 'version', None))

    cipher_suite = _get_cipher_name(getattr(msg, 'cipher', None))
    certificate = None
    for msg in getattr(tls_packet.payload, 'msg', list()):
        if isinstance(msg, TLSCertificate):
            certificate = _parse_certificate(msg)

    return ServerHelloInfo(
        name=msg.__class__.__name__,
        sid=getattr(msg, 'sid', None),
        cipher=cipher_suite,
        version=selected_version,
        certificate=certificate
    )


def _parse_certificate(msg):
    certificate = None
    for cert in msg.certs or []:
        l, v = cert
        common_name = v.subject.get('commonName')
        organization_name = v.issuer.get('organizationName')
        expires = datetime.fromtimestamp(mktime(v.notAfter))
        certificate = Certificate(common_name, organization_name, expires)
        break
    return certificate


def _parse_handshake_message(tls_packet: TLS, msg: Packet) -> ClientHelloInfo | ServerHelloInfo | GenericTlsMessageInfo | Certificate:
    if isinstance(msg, TLSClientHello):
        return _parse_client_hello(msg)
    elif isinstance(msg, TLSServerHello):
        return _parse_server_hello(tls_packet, msg)
    elif isinstance(msg, TLSCertificate):
        certificate = _parse_certificate(msg)
        assert certificate is not None
        return certificate
    else:
        _type = getattr(msg, 'load', [-1])[0]
        msg_class: type = Raw
        if _type == 2:
            msg_class = TLSServerHello
            return _parse_server_hello(tls_packet, msg_class(_remove_key_share_extension(msg.load)))
        elif _type == 1:
            msg_class = TLSClientHello
            return _parse_client_hello(msg_class(_remove_key_share_extension(msg.load)))
        name = msg.__class__.__name__ if isinstance(msg, Packet) else 'UnknownObject'
        return GenericTlsMessageInfo(name=name)


tls_types = {
    0x14: 'Change Cipher Spec',
    0x15: 'Alert',
    0x16: 'Handshake',
    0x17: 'Application Data'
}


def is_tls_packet(data: bytes) -> bool:
    packet_type = False
    if len(data) > 1:
        packet_type = tls_types.get(data[0], None) != None
    return packet_type


def parse_tls_content(content: bytes) -> TlsRecordInfo | None:
    try:
        if is_tls_packet(content):
            tls_packet: Packet = TLS(content)

            if not isinstance(tls_packet, TLS):
                if 'TLS' in tls_packet.__class__.__name__ or 'SSL' in tls_packet.__class__.__name__:
                    logger.debug(f'parsed as non-standard tls/ssl class: {tls_packet.__class__.__name__}')
                    return None
                else:
                    logger.debug('content does not appear to be a tls record')
                    return None

            record_version = _parse_tls_version(getattr(tls_packet, 'version', None))
            record_type = TlsContentType.from_int(getattr(tls_packet, 'type', None))
            parsed_messages: list[ClientHelloInfo | ServerHelloInfo | GenericTlsMessageInfo] = []
            server_hello = None
            certificate = None

            def _append_message(msg: ClientHelloInfo | ServerHelloInfo | GenericTlsMessageInfo | Certificate):
                nonlocal server_hello, certificate

                if isinstance(msg, ServerHelloInfo):
                    server_hello = msg
                    parsed_messages.append(msg)
                elif isinstance(msg, Certificate):
                    certificate = msg
                else:
                    parsed_messages.append(msg)

            def _setup_messages():
                nonlocal server_hello, certificate
                if server_hello is not None and certificate is not None:
                    server_hello.certificate = certificate

            if hasattr(tls_packet, 'msg') and isinstance(tls_packet.msg, list):
                for msg_layer in tls_packet.msg:
                    if record_type == TlsContentType.HANDSHAKE:
                        _append_message(_parse_handshake_message(tls_packet, msg_layer))

                    elif isinstance(msg_layer, TLSChangeCipherSpec):
                        _append_message(GenericTlsMessageInfo(name='ChangeCipherSpec'))
                    elif isinstance(msg_layer, Raw):
                        logger.warning(f'encountered raw message layer inside tls record: {msg_layer.load!r}')
                        _append_message(GenericTlsMessageInfo(name='Raw'))
                    else:
                        name = msg_layer.__class__.__name__ if isinstance(msg_layer, Packet) else 'UnknownObject'
                        _append_message(GenericTlsMessageInfo(name=name))
            _setup_messages()
            return TlsRecordInfo(
                name=tls_packet.__class__.__name__,
                type=record_type,
                version=record_version,
                messages=parsed_messages
            )
        else:
            return None
    except Exception as e:
        logger.exception(f'error parsing tls content: {e}', exc_info=True)
        logger.error(content)
        return None
