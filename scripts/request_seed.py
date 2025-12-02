import requests
from pathlib import Path

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

STUDENT_ID = "YOUR_STUDENT_ID_HERE"
GITHUB_REPO_URL = "https://github.com/aravindpunyamantula/pki-2fa-python"

def load_public_key_text(path: str) -> str:
    pem = Path(path).read_text(encoding="utf-8")
    return pem

def request_seed():
    public_key_pem = load_public_key_text("student_public.pem")

    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": GITHUB_REPO_URL,
        "public_key": public_key_pem,
    }

    resp = requests.post(API_URL, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print("Response:", data)

    if data.get("status") != "success":
        raise RuntimeError(f"API error: {data}")

    encrypted_seed = data["encrypted_seed"].strip()
    Path("encrypted_seed.txt").write_text(encrypted_seed, encoding="utf-8")
    print("Encrypted seed saved to encrypted_seed.txt")

if __name__ == "__main__":
    request_seed()
