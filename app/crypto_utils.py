from pathlib import Path
import base64

from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes, serialization


def load_private_key(path: str = "student_private.pem"):
    data = Path(path).read_bytes()
    return serialization.load_pem_private_key(data, password=None)


def load_public_key(path: str):
    data = Path(path).read_bytes()
    return serialization.load_pem_public_key(data)


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    ciphertext = base64.b64decode(encrypted_seed_b64)

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    hex_seed = plaintext.decode("utf-8").strip()

    if len(hex_seed) != 64:
        raise ValueError("Seed must be 64 hex chars")
    if any(c not in "0123456789abcdef" for c in hex_seed):
        raise ValueError("Seed must be lowercase hex")

    return hex_seed


def sign_message(message: str, private_key) -> bytes:
    message_bytes = message.encode("utf-8")
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext
