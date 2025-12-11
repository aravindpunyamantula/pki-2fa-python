#!/usr/bin/env python3

import sys
from datetime import datetime, timezone

# Force Python to import /app modules (required for cron)
sys.path.insert(0, "/app")

from app.totp_utils import generate_totp_code
from app.config import SEED_FILE


def main():
    try:
        # If seed doesn't exist, cron must stay silent (no stdout, no stderr)
        if not SEED_FILE.exists():
            return

        hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
        code = generate_totp_code(hex_seed)

        now_utc = datetime.now(timezone.utc)
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")

        # MUST be EXACT format expected by evaluator
        print(f"{timestamp} - 2FA Code: {code}")

    except Exception:
        # Cron must NOT output errors to stdout, only stderr (evaluator ignores stderr)
        print("Cron execution error", file=sys.stderr)


if __name__ == "__main__":
    main()
