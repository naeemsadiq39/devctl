import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]

def load_env(strict=True) -> dict:
    """
    Load config from .env or env/dev.env.

    strict=True:
        Requires DO_TOKEN and DEVCTL_DROPLET_ID.
    strict=False:
        Only requires DO_TOKEN.
    """
    candidates = [
        ROOT / ".env",
        ROOT / "env" / "dev.env",
    ]

    data = {}

    # Load from file
    for path in candidates:
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
            break

    # Overlay OS env
    for key in ["DO_TOKEN", "DEVCTL_DROPLET_ID", "DEVCTL_SSH_KEY", "DEVCTL_SSH_USER"]:
        if key in os.environ:
            data[key] = os.environ[key]

    # --- Validation ---
    if "DO_TOKEN" not in data:
        print("Missing DO_TOKEN. Add it first: devctl config")
        sys.exit(1)

    # Only require droplet ID if strict mode
    if strict and "DEVCTL_DROPLET_ID" not in data:
        print("Missing DEVCTL_DROPLET_ID. Run: devctl config")
        sys.exit(1)

    # Defaults
    data.setdefault("DEVCTL_SSH_KEY", "id_rsa")
    data.setdefault("DEVCTL_SSH_USER", "root")
    data.setdefault("DEVCTL_WRITE_SSH_CONFIG", "true")
    data.setdefault("DO_API_BASE", "https://api.digitalocean.com/v2")

    return data
