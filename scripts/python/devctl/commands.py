from .env import load_env
from .api import do_request, wait_for_active
from .ssh import write_ssh_config
from .billing import calculate_billing
from datetime import datetime
import json
import subprocess
import sys


def cmd_dev_up(args):
    cfg = load_env()
    droplet_id = cfg["DEVCTL_DROPLET_ID"]
    print(f"Starting droplet {droplet_id}...")

    do_request(
        "POST",
        f"/droplets/{droplet_id}/actions",
        cfg,
        json={"type": "power_on"},
    )

    print("Waiting for droplet to become active...")
    info = wait_for_active(cfg, droplet_id)
    ip = info["droplet"]["networks"]["v4"][0]["ip_address"]
    print(f"Droplet IP: {ip}")

    if cfg.get("DEVCTL_WRITE_SSH_CONFIG", "true").lower() == "true":
        write_ssh_config(ip, cfg)


def cmd_dev_down(args):
    cfg = load_env()
    droplet_id = cfg["DEVCTL_DROPLET_ID"]
    print(f"Powering off droplet {droplet_id}...")

    do_request(
        "POST",
        f"/droplets/{droplet_id}/actions",
        cfg,
        json={"type": "power_off"},
    )

    print("Droplet powering off.")


def cmd_snapshot(args):
    cfg = load_env()
    droplet_id = cfg["DEVCTL_DROPLET_ID"]

    if args:
        name = args[0]
    else:
        name = f"devctl-snapshot-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    print(f"Creating snapshot '{name}' for droplet {droplet_id}...")

    data = do_request(
        "POST",
        f"/droplets/{droplet_id}/actions",
        cfg,
        json={"type": "snapshot", "name": name},
    )

    print("Snapshot requested.")
    print(json.dumps(data, indent=2))


def cmd_logs(args):
    cfg = load_env()
    droplet_id = cfg["DEVCTL_DROPLET_ID"]

    print("Fetching recent droplet actions...")
    data = do_request(
        "GET",
        f"/droplets/{droplet_id}/actions?per_page=20",
        cfg,
    )

    for act in data.get("actions", []):
        print(
            f"- {act.get('type'):12s} "
            f"{act.get('status'):10s} "
            f"{act.get('completed_at') or act.get('started_at')}"
        )


def cmd_update(args):
    """git pull if repo cloned"""
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]

    if not (ROOT / ".git").exists():
        print("Not a git repo. Please update manually.")
        return

    print("Running: git pull")
    try:
        subprocess.check_call(["git", "-C", str(ROOT), "pull"])
    except subprocess.CalledProcessError as e:
        print(f"git pull failed: {e}")
        sys.exit(e.returncode)


def cmd_do_bill():
    calculate_billing()
