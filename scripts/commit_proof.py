import base64

from app.crypto_utils import load_private_key, load_public_key, sign_message, encrypt_with_public_key

def main():
    commit_hash = input("Enter commit hash (40-char hex): ").strip()
    if len(commit_hash) != 40:
        raise ValueError("Commit hash must be 40 characters")

    private_key = load_private_key("student_private.pem")
    instructor_pub = load_public_key("instructor_public.pem")

    signature = sign_message(commit_hash, private_key)
    encrypted_sig = encrypt_with_public_key(signature, instructor_pub)

    b64 = base64.b64encode(encrypted_sig).decode("utf-8")
    print("Encrypted commit signature (single line):")
    print(b64)

if __name__ == "__main__":
    main()
