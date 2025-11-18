from pathlib import Path
import sys
from .api import do_request
from .api import tag_droplet

from .env import ROOT, load_env

def cmd_config():
    print("=== devctl configuration ===\n")

    # --- Step 1: SSH key selection ---
    ssh_dir = Path.home() / ".ssh"
    keys = list(ssh_dir.glob("*.pub"))

    if not keys:
        print("No SSH keys found in ~/.ssh")
        print("Generate one: ssh-keygen -t ed25519")
        sys.exit(1)

    print("Available SSH keys:\n")
    for i, key in enumerate(keys, 1):
        print(f"{i}. {key.name}")

    while True:
        sel = input("\nChoose SSH key: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(keys):
            break

    key_pub = keys[int(sel)-1]
    key_private = key_pub.with_suffix("")  # remove .pub

    print(f"Selected SSH key: {key_private.name}\n")

    # --- Step 2: DigitalOcean droplet selection ---
    cfg = load_env(strict=False)  # only DO_TOKEN needed here

    print("Fetching droplets...")
    data = do_request("GET", "/droplets?per_page=100", cfg)
    droplets = data.get("droplets", [])

    if not droplets:
        print("No droplets found.")
        sys.exit(1)

    print("\nAvailable droplets:")
    for i, d in enumerate(droplets, 1):
        size = d.get("size", {})
        print(f"{i}. {d['name']} (ID {d['id']}) — {size.get('vcpus')} CPU, {size.get('memory')}MB, ${size.get('price_monthly')}/mo")

    while True:
        sel = input("\nChoose droplet: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(droplets):
            break

    droplet = droplets[int(sel)-1]
    droplet_id = droplet["id"]
    print(f"\nSelected droplet: {droplet['name']} ({droplet_id})\n")

    # --- Step 2.5: Tag droplet ---
    tag_name = "devctl"
    tag_droplet(cfg, droplet_id, tag_name)
    print(f"Tag '{tag_name}' applied.\n")

    # --- Step 3: Write .env ---
    env_path = ROOT / ".env"

    new_env = (
        f"DO_TOKEN={cfg['DO_TOKEN']}\n"
        f"DEVCTL_DROPLET_ID={droplet_id}\n"
        f"DEVCTL_SSH_KEY={key_private.name}\n"
        f"DEVCTL_SSH_USER=root\n"
    )

    env_path.write_text(new_env)
    print("Configuration saved:\n")
    print(new_env)
    print("Done.")
