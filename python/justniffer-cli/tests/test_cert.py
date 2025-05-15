# Import necessary libraries
# You might need to install cryptography: pip install cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID, ExtensionOID, AuthorityInformationAccessOID
from cryptography.hazmat.primitives import serialization
import datetime
import binascii # To display bytes nicely

# The binary data provided by the user
# This represents a TLS record containing a Certificate message
tls_data = b'\x16\x03\x03\x00j\x02\x00\x00f\x03\x03\xe0\xb9DT\x8e\xda\xfa\xb2\x88:\xe6W\x04\xfe\xc2\xd8\xa0\xa8\xd8\xb4\xd4o\xbdwgL\xff\x9cX\x8e\xe7\xda g\x94\xdfoS\xfe\x93\xdb:7P\r=\xf0M\x88i2\xcd\xd4\x1b\xf0\xfb\xf3\xfc\xfe\xd1\x96\xf6\xdc\x88v\xc00\x00\x00\x1e\xff\x01\x00\x01\x00\x00\x00\x00\x00\x00\x0b\x00\x04\x03\x00\x01\x02\x00\x10\x00\x05\x00\x03\x02h2\x00\x17\x00\x00\x16\x03\x03\n\xa5\x0b\x00\n\xa1\x00\n\x9e\x00\x05\x8e0\x82\x05\x8a0\x82\x04r\xa0\x03\x02\x01\x02\x02\x12\x05\xe7\xa2\x85\x0e\xbe\xe9x\x10m\xd3\xe6\x028\xc7\x1b\x86\x1d0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x0b\x05\x00031\x0b0\t\x06\x03U\x04\x06\x13\x02US1\x160\x14\x06\x03U\x04\n\x13\rLet\'s Encrypt1\x0c0\n\x06\x03U\x04\x03\x13\x03R110\x1e\x17\r250323170525Z\x17\r250621170524Z0\x191\x170\x15\x06\x03U\x04\x03\x13\x0eboneragroup.it0\x82\x01"0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82\x01\n\x02\x82\x01\x01\x00\x9e\xbc8\xae \xf4\xcf\xc0A\xd9\x1d\xda\x1cS\xd7Q\xd6A#\xcf\xab\x97K\xfc\xd3\x11}\xc6\xa4t\xcax\xfc\xc9\xf6\xea\xfd\xaa\x13nBZ\xc7\x9b\x96\x9f\x97Q\xb5Q\xfd\xf3u\x99\xfep\xc7\xa3i\xc0\xf9D\xae!\xb9d\x13h\x82l6\xc8\xaa,\xff\xe2eHQ\xe5.\xe8\xc0A\xeb\xfe\xbby\x1fY\x83%\xab~S~*t\x98\x9e\x86=(\x92\xc94\x80]\x82\xee\x1bf>\x03\xf5\xca\x04\xf0\t\x8c\x94\x14\xccP\xc5\xc1\xe3w|\xf9S\xe5*-v\x81\x864\xf1\x90\x83.\xac\xba\xb4\xbe\xfd\x90\xa6\x134O\x9b\xd7\x97\xdd\x1b\xda\x85\x96\xff\xd0\x19\xf7\x94\xd5\xdd\xc3S\x08\xb7q\xad{\xe2\xdd\xa9}?\x11\xaaSv\xa1J\xadFQ\x8d\x1a)y\x07\xadV\xec\xe2\x9f\xfc\x17\x96}\x96\xbe\x91\xc9\xf5_\xd1>\xae6\xb2\n\xa1Yk\x80/\x9b\xd2\x97\xfe\xa6\xb3\xfc\x19\'m\x81\xcaP\xed1v&\xb9\xf1vg\x16\xeb\xb4g\xa2\xd5}\x83\xcab\xc5L\x04\xfa\xe6\xa9\x02\x03\x01\x00\x01\xa3\x82\x02\xb00\x82\x02\xac0\x0e\x06\x03U\x1d\x0f\x01\x01\xff\x04\x04\x03\x02\x05\xa00\x1d\x06\x03U\x1d%\x04\x160\x14\x06\x08+\x06\x01\x05\x05\x07\x03\x01\x06\x08+\x06\x01\x05\x05\x07\x03\x020\x0c\x06\x03U\x1d\x13\x01\x01\xff\x04\x020\x000\x1d\x06\x03U\x1d\x0e\x04\x16\x04\x14\x1e\xc0\xa4\x92\x1b\x9d\x082\x91\x1cLS\xd9\xd5\x90\x1c\x07d\xd2\x970\x1f\x06\x03U\x1d#\x04\x180\x16\x80\x14\xc5\xcfF\xa4\xea\xf4\xc3\xc0zl\x95\xc4-\xb0^\x92/&\xe3\xb90W\x06\x08+\x06\x01\x05\x05\x07\x01\x01\x04K0I0"\x06\x08+\x06\x01\x05\x05\x070\x01\x86\x16http://r11.o.lencr.org0#\x06\x08+\x06\x01\x05\x05\x070\x02\x86\x17http://r11.i.lencr.org/0\x81\x85\x06\x03U\x1d\x11\x04~0|\x82\tbonera.it\x82\x0fbonera2ruote.it\x82\x0eboneragroup.it\x82\x16service.boneragroup.it\x82\rwww.bonera.it\x82\x13www.bonera2ruote.it\x82\x12www.boneragroup.it0\x13\x06\x03U\x1d \x04\x0c0\n0\x08\x06\x06g\x81\x0c\x01\x02\x010.\x06\x03U\x1d\x1f\x04\'0%0#\xa0!\xa0\x1f\x86\x1dhttp://r11.c.lencr.org/30.crl0\x82\x01\x05\x06\n+\x06\x01\x04\x01\xd6y\x02\x04\x02\x04\x81\xf6\x04\x81\xf3\x00\xf1\x00v\x00\x13J\xdf\x1a\xb5\x98B\tx\x0co\xefLz\x91\xa4\x16\xb7#I\xceXWj\xdf\xae\xda\xa7\xc2\xab\xe0"\x00\x00\x01\x95\xc4,\xf5&\x00\x00\x04\x03\x00G0E\x02!\x00\x8c}qA\xe2I\xe8V\xd3(\x89\x11_\xff\xbbC\xaa\xa5\x8f/\x1d\x0bM\xb3\x0f\x04\xa3K=\x83\xa2\x9c\x02 88\x95\xa8\x8f\xda\xa1o\xaf\xdc\xd1\xe8\xea-\xcd\xd7\xa5\x96\x914?\x16\x8d"\xbd\x9b-j2\xd0\xa0$\x00w\x00\xcf\x11V\xee\xd5.|\xaf\xf3\x87[\xd9i.\x9b\xe9\x1aqgJ\xb0\x17\xec\xac\x01\xd2[w\xce\xcc;\x08\x00\x00\x01\x95\xc4,\xfc{\x00\x00\x04\x03\x00H0F\x02!\x00\xb1\xf3;\xbe\xad\x15W\xb4\x177\x11\xa7|\x04\xd8\xc3\x13\x04\xda\xea\x81\x1d\xd1C0\xcc2\xe1\xed\r\n\xe7\x02!\x00\x96xR\xf3XZ\x81\\\xd2e\x9e,\r\x7fL\xae\x8f\xfd\xe1\x0f\xb9W\xecOfT@\xed\x02\xea\r\xa90\r\x06\t*\x86H\x86\xf7\r\x01\x01\x0b\x05\x00\x03\x82\x01\x01\x00\x17\x035FD\x92\xb3?\x06\x97\xc1\xef\xdc%\xd2\xcd\x12L\x9eB\xc1\xe2\xe3\x18\xb7\x82\xd8u\xf9i+{\x8e o:\x10\x91\xd2\xf2\xf3\x05\x1b\x98\xca\x14\x853\x9b\x029\x02&\xfb!@' 


def extract_certificate_details(data: bytes):
    try:
        # --- Locate the Certificate Data ---
        # This logic assumes the certificate is in the second TLS record provided
        # and follows the structure: TLS Record Header -> Handshake Header ->
        # Certificate List Length -> Certificate Length -> Certificate Data.
        # This is based on analyzing the specific input data. A more robust parser
        # would fully decode the TLS record layers.

        # Find the start of the Certificate handshake message (type 0x0b)
        # We search for the sequence marking the second record and the cert message
        # \x16\x03\x03...\x0b
        cert_msg_header_start = -1
        # Look for the second record header (\x16\x03\x03) after the first one
        first_record_end = data.find(b'\x16\x03\x03', 1)
        if first_record_end != -1:
            # Look for the certificate message type (0x0b) after the record header
            # Handshake header: type(1) + length(3) = 4 bytes offset from msg start
            cert_type_offset = first_record_end + 5 # 5 bytes for record header
            if data[cert_type_offset] == 0x0b: # Check if it's a Certificate message
                 cert_msg_header_start = cert_type_offset

        if cert_msg_header_start == -1:
            print("Error: Could not reliably locate the Certificate handshake message start.")
            # Fallback attempt: Find the common start sequence of a large DER cert
            # This is less reliable but might work in some cases.
            der_start_seq = b'0\x82' # SEQUENCE tag + 2-byte length common for certs
            cert_start_index = data.find(der_start_seq, 100) # Search after potential headers
            if cert_start_index == -1:
                 print("Error: Could not find DER start sequence '0\\x82'. Cannot extract certificate.")
                 return
            # Estimating length is difficult here without parsing TLS headers
            # We'll try loading from this point and hope cryptography handles it.
            # This is NOT robust.
            print("Warning: Using fallback method to find certificate start. May be inaccurate.")
            der_data = data[cert_start_index:]
            cert_len = len(der_data) # Assume rest of data might be the cert

        else:
            # Calculate offsets based on the found Certificate message header
            certs_list_len_start = cert_msg_header_start + 1 + 3 # Skip type and length
            first_cert_len_start = certs_list_len_start + 3    # Skip list length
            first_cert_data_start = first_cert_len_start + 3   # Skip cert length

            # Check if calculated indices are within bounds
            if first_cert_data_start >= len(data):
                 print("Error: Calculated certificate start index is out of bounds.")
                 return

            # Extract the length of the first certificate (3-byte big-endian)
            cert_len_bytes = data[first_cert_len_start:first_cert_len_start + 3]
            cert_len = int.from_bytes(cert_len_bytes, byteorder='big')

            # Check if length is plausible
            if first_cert_data_start + cert_len > len(data):
                 print(f"Error: Calculated certificate length ({cert_len}) exceeds data boundary.")
                 return

            # Extract the DER encoded certificate data for the first certificate
            der_data = data[first_cert_data_start : first_cert_data_start + cert_len]
            print(f"Successfully located certificate data at index {first_cert_data_start} with length {cert_len}.")


        # --- Parse the Certificate ---
        # Load the DER-encoded certificate
        cert = x509.load_der_x509_certificate(der_data)

        # --- Extract and Print Information ---
        print("-" * 30)
        print("Certificate Details")
        print("-" * 30)

        # Subject
        print("Subject:")
        for attribute in cert.subject:
            print(f"  {attribute.oid._name}: {attribute.value}")

        # Issuer
        print("\nIssuer:")
        for attribute in cert.issuer:
            print(f"  {attribute.oid._name}: {attribute.value}")

        # Validity Period
        print("\nValidity:")
        # Use astimezone(None) to convert to local time for display
        print(f"  Not Valid Before: {cert.not_valid_before_utc.astimezone(None).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  Not Valid After:  {cert.not_valid_after_utc.astimezone(None).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        # Check current validity
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        is_valid = cert.not_valid_before_utc <= now_utc <= cert.not_valid_after_utc
        validity_status = 'Yes' if is_valid else 'No'
        if not is_valid:
            if now_utc < cert.not_valid_before_utc:
                validity_status += " (Not yet valid)"
            else:
                validity_status += " (Expired)"
        print(f"  Currently Valid (UTC): {validity_status}")


        # Serial Number
        print(f"\nSerial Number: {cert.serial_number}")

        # Signature Algorithm
        print(f"\nSignature Algorithm: {cert.signature_algorithm_oid._name}")

        # Public Key Information
        public_key = cert.public_key()
        try:
            # Get key type name cleanly
            key_type = type(public_key).__name__.replace("_PublicKey", "").replace("PublicKey", "")
            print(f"\nPublic Key Type: {key_type}")
            print(f"  Key Size: {public_key.key_size} bits")
            # Optionally print public key bytes (PEM format is readable)
            # pem_key = public_key.public_bytes(
            #     encoding=serialization.Encoding.PEM,
            #     format=serialization.PublicFormat.SubjectPublicKeyInfo
            # )
            # print(f"  Public Key (PEM):\n{pem_key.decode('ascii')}")
        except Exception as pk_e:
            print(f"\nCould not get full public key details: {pk_e}")


        # Extensions
        print("\nExtensions:")
        try:
            for ext in cert.extensions:
                print(f"  OID: {ext.oid.dotted_string} ({ext.oid._name or 'Unknown'})")
                print(f"  Critical: {ext.critical}")
                ext_value = ext.value # Cache value for easier access

                # Subject Alternative Name (SAN)
                if ext.oid == ExtensionOID.SUBJECT_ALTERNATIVE_NAME:
                    print("    Subject Alternative Names:")
                    try:
                        for name in ext_value.get_values_for_type(x509.DNSName):
                            print(f"      DNS: {name}")
                        for name in ext_value.get_values_for_type(x509.IPAddress):
                             print(f"      IP Address: {name}")
                        # Add other types if needed (DirectoryName, RFC822Name, etc.)
                    except Exception as san_e:
                         print(f"      Error parsing SAN values: {san_e}")

                # Authority Key Identifier (AKI)
                elif ext.oid == ExtensionOID.AUTHORITY_KEY_IDENTIFIER:
                    print("    Authority Key Identifier:")
                    if ext_value.key_identifier:
                        print(f"      Key Identifier: {ext_value.key_identifier.hex()}")
                    if ext_value.authority_cert_issuer:
                         print(f"      Authority Cert Issuer:")
                         for name in ext_value.authority_cert_issuer:
                              # This is a list of GeneralName objects
                              print(f"        {name.type}: {name.value}")
                    if ext_value.authority_cert_serial_number:
                         print(f"      Authority Cert Serial Number: {ext_value.authority_cert_serial_number}")

                # Subject Key Identifier (SKI)
                elif ext.oid == ExtensionOID.SUBJECT_KEY_IDENTIFIER:
                    print(f"    Subject Key Identifier: {ext_value.digest.hex()}")

                # Key Usage
                elif ext.oid == ExtensionOID.KEY_USAGE:
                    usages = [
                        "digital_signature", "content_commitment", "key_encipherment",
                        "data_encipherment", "key_agreement", "key_cert_sign",
                        "crl_sign", "encipher_only", "decipher_only"
                    ]
                    print("    Key Usages:")
                    active_usages = [usage for usage in usages if getattr(ext_value, usage, False)]
                    if active_usages:
                        for usage in active_usages:
                             print(f"      - {usage}")
                    else:
                        print("      (No specific usages)")


                # Extended Key Usage (EKU)
                elif ext.oid == ExtensionOID.EXTENDED_KEY_USAGE:
                    print("    Extended Key Usages:")
                    if ext_value:
                         for usage_oid in ext_value:
                             print(f"      - {usage_oid._name or usage_oid.dotted_string}")
                    else:
                         print("      (No specific usages)")


                # Certificate Policies
                elif ext.oid == ExtensionOID.CERTIFICATE_POLICIES:
                     print("    Certificate Policies:")
                     if ext_value:
                         for policy_info in ext_value:
                             print(f"      Policy ID: {policy_info.policy_identifier.dotted_string} ({policy_info.policy_identifier._name or 'Unknown'})")
                             if policy_info.policy_qualifiers:
                                 for qualifier in policy_info.policy_qualifiers:
                                     # Usually CPS URI or User Notice
                                     if isinstance(qualifier, x509.UserNotice):
                                          notice_ref = qualifier.notice_reference
                                          notice_text = qualifier.explicit_text
                                          print("        User Notice:")
                                          if notice_ref:
                                               print(f"          Organization: {notice_ref.organization}")
                                               print(f"          Notice Numbers: {notice_ref.notice_numbers}")
                                          if notice_text:
                                               print(f"          Explicit Text: {notice_text}")
                                     elif isinstance(qualifier, str): # Assumed to be CPS URI
                                          print(f"        CPS URI: {qualifier}")
                                     else:
                                          print(f"        Qualifier: {qualifier}") # Raw qualifier data
                     else:
                         print("      (No policies listed)")


                # Authority Information Access (AIA)
                elif ext.oid == ExtensionOID.AUTHORITY_INFORMATION_ACCESS:
                    print("    Authority Information Access:")
                    if ext_value:
                         for desc in ext_value:
                             method_name = desc.access_method._name or desc.access_method.dotted_string
                             location_value = desc.access_location.value
                             print(f"      Access Method: {method_name}")
                             print(f"      Access Location ({type(desc.access_location).__name__}): {location_value}")
                    else:
                         print("      (No AIA specified)")


                # CRL Distribution Points
                elif ext.oid == ExtensionOID.CRL_DISTRIBUTION_POINTS:
                    print("    CRL Distribution Points:")
                    if ext_value:
                         for dist_point in ext_value:
                             if dist_point.full_name:
                                 for general_name in dist_point.full_name:
                                      print(f"      URI ({type(general_name).__name__}): {general_name.value}")
                             if dist_point.relative_name:
                                 print(f"      Relative Name: {dist_point.relative_name}")
                             if dist_point.reasons:
                                 print(f"      Reasons: {dist_point.reasons}")
                             if dist_point.crl_issuer:
                                 print(f"      CRL Issuer:")
                                 for name in dist_point.crl_issuer:
                                     print(f"        {name.type}: {name.value}")
                    else:
                         print("      (No CRL DP specified)")

                # Basic Constraints (indicates if it's a CA)
                elif ext.oid == ExtensionOID.BASIC_CONSTRAINTS:
                     print(f"    Basic Constraints:")
                     print(f"      CA: {ext_value.ca}")
                     if ext_value.ca and ext_value.path_length is not None:
                         print(f"      Path Length Constraint: {ext_value.path_length}")
                     elif ext_value.ca:
                          print(f"      Path Length Constraint: None")


                # --- Add more specific extension handling here if needed ---

                # Generic fallback for unhandled extensions
                else:
                     try:
                         # Try to get raw bytes if value has no standard representation
                         raw_bytes = getattr(ext_value, 'value', None) # OCSPNonce, etc.
                         if isinstance(raw_bytes, bytes):
                              print(f"    Value (hex): {binascii.hexlify(raw_bytes).decode()}")
                         else:
                              print(f"    Value: {ext_value}") # Standard repr
                     except Exception:
                         print(f"    Value: {ext_value}") # Fallback

        except x509.ExtensionNotFound:
            print("  No extensions found or error parsing extensions.")
        except Exception as ext_e:
            print(f"  Error processing extensions: {ext_e}")


        print("-" * 30)

    except ImportError:
        print("Error: The 'cryptography' library is required.")
        print("Please install it using: pip install cryptography")
    except ValueError as e:
        # This often happens if the DER data is incorrect/incomplete
        print(f"Error parsing certificate data: {e}")
        print("Ensure the located/extracted data is a valid DER-encoded certificate.")
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred: {e}")
        # print(traceback.format_exc()) # Uncomment for detailed debugging


# --- Run the extraction ---
def test():
    extract_certificate_details(tls_data)

if __name__ == "__main__":
    test()