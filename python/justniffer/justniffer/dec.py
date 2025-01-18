from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

def decript_data_file(decripted_file: str, key: RSAPrivateKey) -> bytes:
    with open(decripted_file, 'rb') as data_file:
        data = data_file.read()
        breakpoint()
        return key.decrypt(data, padding=PKCS1v15())

def read_private_key(filename: str) -> PrivateKeyTypes:

    with open(filename, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # or provide the password if the key is encrypted
            backend=default_backend()
        )

    return private_key
