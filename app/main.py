from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path

from .crypto_utils import load_private_key, decrypt_seed
from .totp_utils import generate_totp_code, verify_totp_code, seconds_remaining_in_period
from .config import SEED_FILE, DATA_DIR

app = FastAPI(title="PKI 2FA Microservice")


class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Verify2FARequest(BaseModel):
    code: str | None = None


@app.on_event("startup")
def ensure_directories():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    try:
        private_key = load_private_key("student_private.pem")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Private key load failed: {e}")

    try:
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")

    try:
        SEED_FILE.write_text(hex_seed + "\n", encoding="utf-8")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to persist seed")

    return {"status": "ok"}


@app.get("/generate-2fa")
def generate_2fa():
    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    try:
        hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        raise HTTPException(status_code=500, detail="Error reading seed")

    try:
        code = generate_totp_code(hex_seed)
        valid_for = seconds_remaining_in_period(30)
    except Exception:
        raise HTTPException(status_code=500, detail="Error generating TOTP")

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
def verify_2fa(body: Verify2FARequest):
    if body.code is None or body.code.strip() == "":
        raise HTTPException(status_code=400, detail="Missing code")

    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    try:
        hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        raise HTTPException(status_code=500, detail="Error reading seed")

    try:
        valid = verify_totp_code(hex_seed, body.code, valid_window=1)
    except Exception:
        raise HTTPException(status_code=500, detail="Error verifying TOTP")

    return {"valid": valid}
