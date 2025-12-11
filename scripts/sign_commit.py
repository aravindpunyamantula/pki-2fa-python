#!/usr/bin/env python3
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


# ---- CONFIG ----
COMMIT_HASH = "2212ccf53fbd03a2e88606dfd16e84ec6fcb8552"

STUDENT_PRIVATE_KEY_FILE = "student_private.pem"
INSTRUCTOR_PUBLIC_KEY_FILE = "instructor_public.pem"
# ----------------


def load_private_key(path: str):
    return serialization.load_pem_private_key(
        Path(path).read_bytes(),
        password=None,
    )


def load_public_key(path: str):
    return serialization.load_pem_public_key(
        Path(path).read_bytes()
    )


def sign_commit_hash(commit_hash: str, private_key):
    """
    Sign ASCII commit hash using RSA-PSS + SHA256 (max salt length)
    """
    msg_bytes = commit_hash.encode("utf-8")

    signature = private_key.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature


def encrypt_for_instructor(signature: bytes, instructor_pubkey):
    """
    Encrypt signature with instructor public key using RSA-OAEP + SHA256
    """
    encrypted = instructor_pubkey.encrypt(
        signature,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return encrypted


def main():
    print("Loading keys...")
    private_key = load_private_key(STUDENT_PRIVATE_KEY_FILE)
    instructor_pubkey = load_public_key(INSTRUCTOR_PUBLIC_KEY_FILE)

    print("Signing commit hash...")
    signature = sign_commit_hash(COMMIT_HASH, private_key)

    print("Encrypting signature...")
    encrypted_sig = encrypt_for_instructor(signature, instructor_pubkey)

    # Base64 encode
    encrypted_sig_b64 = base64.b64encode(encrypted_sig).decode("utf-8")

    print("\n----- FINAL SUBMISSION OUTPUT -----")
    print(f"Commit Hash: {COMMIT_HASH}")
    print(f"Encrypted Signature (Base64):\n{encrypted_sig_b64}")
    print("-----------------------------------\n")

    # Save to file for convenience
    Path("commit_proof.txt").write_text(encrypted_sig_b64, encoding="utf-8")
    print("Saved commit_proof.txt")


if __name__ == "__main__":
    main()
