import base64
import time

import pyotp


def hex_to_base32(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    b32 = base64.b32encode(seed_bytes).decode("utf-8")
    return b32


def generate_totp_code(hex_seed: str) -> str:
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.verify(code, valid_window=valid_window)


def seconds_remaining_in_period(interval: int = 30) -> int:
    now = int(time.time())
    return interval - (now % interval)
