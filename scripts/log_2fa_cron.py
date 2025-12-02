#!/usr/bin/env python3
import sys
from datetime import datetime, timezone

from app.totp_utils import generate_totp_code
from app.config import SEED_FILE

def main():
    try:
        if not SEED_FILE.exists():
            print("Seed file not found", file=sys.stderr)
            return

        hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
        code = generate_totp_code(hex_seed)

        now_utc = datetime.now(timezone.utc)
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")

        print(f"{timestamp} - 2FA Code: {code}")
    except Exception as e:
        print(f"Error in cron script: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
