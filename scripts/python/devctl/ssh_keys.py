import sys
import subprocess
from pathlib import Path
from .api import do_request
from .env import load_env
from .api import get_droplet_ip

def ssh_list(cfg=None):
    if cfg is None:
        cfg = load_env(strict=False)

    print("Fetching DigitalOcean SSH keys...")
    data = do_request("GET", "/account/keys", cfg)
    keys = data.get("ssh_keys", [])

    if not keys:
        print("No SSH keys found on DigitalOcean.")
        return

    print("\nDigitalOcean SSH Keys:")
    for k in keys:
        print(f"- ID {k['id']} | {k['name']} | {k['public_key'][:40]}...")
    print()


def ssh_add(args):
    if not args:
        print("Usage: devctl ssh add <path-to-public-key>")
        sys.exit(1)

    key_path = Path(args[0]).expanduser()
    if not key_path.exists():
        print(f"Key not found: {key_path}")
        sys.exit(1)

    pubkey = key_path.read_text().strip()
    cfg = load_env(strict=False)

    print(f"Uploading SSH key '{key_path.name}' to DigitalOcean...")

    body = {
        "name": key_path.stem,
        "public_key": pubkey
    }

    data = do_request("POST", "/account/keys", cfg, json=body)
    print(f"Added SSH key with ID {data['ssh_key']['id']}")
    print()


def ssh_delete(args):
    cfg = load_env(strict=False)
    print("Fetching DigitalOcean SSH keys...")

    data = do_request("GET", "/account/keys", cfg)
    keys = data.get("ssh_keys", [])

    if not keys:
        print("No SSH keys to delete.")
        return

    print("\nSelect a key to delete:")
    for i, k in enumerate(keys, 1):
        print(f"{i}. {k['name']} (ID {k['id']})")

    sel = input("\nChoose: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(keys)):
        print("Invalid selection")
        return

    key = keys[int(sel) - 1]

    confirm = input(f"Delete SSH key '{key['name']}' (ID {key['id']})? y/N ").lower()
    if confirm != "y":
        print("Cancelled.")
        return

    do_request("DELETE", f"/account/keys/{key['id']}", cfg)

    print("Key deleted.\n")


def ssh_sync(args):
    """
    Ensures the SSH key specified in .env exists in DigitalOcean.
    If missing → uploads automatically.
    """
    cfg = load_env(strict=False)
    ssh_key = cfg["DEVCTL_SSH_KEY"]
    key_path = Path.home() / ".ssh" / f"{ssh_key}.pub"

    if not key_path.exists():
        print(f"Local SSH key not found: {key_path}")
        sys.exit(1)

    pubkey = key_path.read_text().strip()

    print(f"Syncing SSH key '{ssh_key}' to DigitalOcean...")

    # Check existing keys
    data = do_request("GET", "/account/keys", cfg)
    keys = data.get("ssh_keys", [])

    for k in keys:
        if k["public_key"].strip() == pubkey.strip():
            print("SSH key already exists in DigitalOcean.")
            return

    # Upload missing key
    body = {
        "name": ssh_key,
        "public_key": pubkey
    }

    result = do_request("POST", "/account/keys", cfg, json=body)
    print(f"SSH key uploaded with ID {result['ssh_key']['id']}\n")

def ssh_attach(args):
    """
    Attach a local SSH public key to the droplet by adding it
    to /root/.ssh/authorized_keys via SSH.
    """

    cfg = load_env()
    droplet_id = cfg["DEVCTL_DROPLET_ID"]

    # Get droplet public IP
    ip = get_droplet_ip(cfg, droplet_id)

    # Pick key
    if not args:
        ssh_key = cfg["DEVCTL_SSH_KEY"]
        pub = Path.home() / ".ssh" / f"{ssh_key}.pub"
    else:
        pub = Path(args[0]).expanduser()

    if not pub.exists():
        print(f"SSH public key not found: {pub}")
        sys.exit(1)

    public_key = pub.read_text().strip()
    print(f"Pushing SSH key '{pub.name}' → droplet {ip}")

    # Push key via SSH
    cmd = [
        "ssh",
        f"root@{ip}",
        f'echo "{public_key}" >> /root/.ssh/authorized_keys'
    ]

    subprocess.run(cmd, check=True)
    print("SSH key attached to droplet.\n")

def ssh_login(args):
    cfg = load_env()
    droplet_id = cfg["DEVCTL_DROPLET_ID"]
    ssh_key = cfg["DEVCTL_SSH_KEY"]

    ip = get_droplet_ip(cfg, droplet_id)

    key_path = Path.home() / ".ssh" / ssh_key

    cmd = [
        "ssh",
        f"root@{ip}",
        "-i",
        str(key_path)
    ]

    print(f"Connecting to droplet {droplet_id} ({ip})...")
    subprocess.run(cmd)
