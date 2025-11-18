#!/usr/bin/env python3
import os
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import subprocess

try:
    import requests
except ImportError:
    print("devctl requires the 'requests' library. Install it with:")
    print("  pip install requests")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[2]
VERSION_FILE = ROOT / "VERSION"


def read_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    return "0.0.0-dev"


def load_env() -> dict:
    """
    Load config from .env or env/dev.env
    Simple key=value parser, ignores comments and blank lines.
    """
    candidates = [
        ROOT / ".env",
        ROOT / "env" / "dev.env",
    ]

    data = {}
    for path in candidates:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                data[key.strip()] = val.strip()
            break

    # Overlay real environment on top (env vars override file)
    for key in ["DO_TOKEN", "DO_DROPLET_ID", "DO_API_BASE",
                "DEVCTL_WRITE_SSH_CONFIG", "DEVCTL_SSH_USER", "DEVCTL_SSH_PORT"]:
        if key in os.environ:
            data[key] = os.environ[key]

    # Defaults
    data.setdefault("DO_API_BASE", "https://api.digitalocean.com/v2")
    data.setdefault("DEVCTL_WRITE_SSH_CONFIG", "true")
    data.setdefault("DEVCTL_SSH_USER", "root")
    data.setdefault("DEVCTL_SSH_PORT", "22")

    missing = [k for k in ("DO_TOKEN", "DO_DROPLET_ID") if k not in data or not data[k]]
    if missing:
        print(f"Missing required config keys in .env: {', '.join(missing)}")
        sys.exit(1)

    return data


def do_request(method: str, path: str, cfg: dict, **kwargs):
    url = cfg["DO_API_BASE"].rstrip("/") + path
    headers = {
        "Authorization": f"Bearer {cfg['DO_TOKEN']}",
        "Content-Type": "application/json",
    }
    resp = requests.request(method, url, headers=headers, **kwargs)
    if not resp.ok:
        print(f"[ERROR] {method} {url} -> {resp.status_code}")
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
        sys.exit(1)
    if resp.text.strip():
        return resp.json()
    return {}


def wait_for_active(cfg: dict, droplet_id: str, timeout_sec: int = 300) -> dict:
    start = time.time()
    while True:
        data = do_request("GET", f"/droplets/{droplet_id}", cfg)
        status = data["droplet"]["status"]
        print(f"Status: {status}")
        if status == "active":
            return data
        if time.time() - start > timeout_sec:
            print("Timed out waiting for droplet to become active.")
            sys.exit(1)
        time.sleep(3)


def cmd_dev_up(args: list) -> None:
    cfg = load_env()
    droplet_id = cfg["DO_DROPLET_ID"]
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


def write_ssh_config(ip: str, cfg: dict) -> None:
    ssh_user = cfg.get("DEVCTL_SSH_USER", "root")
    ssh_port = cfg.get("DEVCTL_SSH_PORT", "22")

    home = Path(os.path.expanduser("~"))
    ssh_dir = home / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    config_file = ssh_dir / "config"

    block = (
        "Host devctl\n"
        f"    HostName {ip}\n"
        f"    User {ssh_user}\n"
        f"    Port {ssh_port}\n"
        f"    IdentityFile {ssh_dir / 'id_rsa'}\n"
    )

    existing = ""
    if config_file.exists():
        existing = config_file.read_text(encoding="utf-8")

    # naive replace of previous devctl block
    lines = existing.splitlines()
    new_lines = []
    skip = False
    for line in lines:
        if line.strip().lower().startswith("host devctl"):
            skip = True
            continue
        if skip and line.startswith("Host "):
            skip = False
        if not skip:
            new_lines.append(line)
    if new_lines and new_lines[-1] != "":
        new_lines.append("")
    new_lines.append(block.rstrip("\n"))
    config_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Updated SSH config at {config_file} (Host devctl).")


def cmd_dev_down(args: list) -> None:
    cfg = load_env()
    droplet_id = cfg["DO_DROPLET_ID"]
    print(f"Powering off droplet {droplet_id}...")
    do_request(
        "POST",
        f"/droplets/{droplet_id}/actions",
        cfg,
        json={"type": "power_off"},
    )
    print("Droplet powering off.")


def cmd_do_bill(args: list) -> None:
    cfg = load_env()
    droplet_id = cfg["DO_DROPLET_ID"]
    hourly_rate = float(os.environ.get("DEVCTL_RATE", "0.071"))
    monthly_cap = float(os.environ.get("DEVCTL_CAP", "48"))

    print("Fetching droplet actions...")
    actions = []
    page = 1
    while True:
        data = do_request(
            "GET",
            f"/droplets/{droplet_id}/actions?per_page=200&page={page}",
            cfg,
        )
        batch = data.get("actions", [])
        if not batch:
            break
        actions.extend(batch)
        if "next" not in data.get("links", {}).get("pages", {}):
            break
        page += 1

    # Sort actions by completion time
    actions.sort(key=lambda a: a.get("completed_at") or a.get("started_at") or "")

    def parse_iso(ts: str):
        if ts is None:
            return None
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)

    total_seconds = 0
    current_start = None

    for act in actions:
        atype = act.get("type")
        status = act.get("status")
        completed = parse_iso(act.get("completed_at"))
        started = parse_iso(act.get("started_at"))

        if atype == "power_on" and status == "completed":
            current_start = completed or started
        elif atype == "power_off" and status == "completed" and current_start:
            end_time = completed or started
            if end_time:
                total_seconds += (end_time - current_start).total_seconds()
            current_start = None

    if current_start:
        now = datetime.now(timezone.utc)
        total_seconds += (now - current_start).total_seconds()

    hours = total_seconds / 3600.0
    cost = hours * hourly_rate

    print("\n📊 DigitalOcean Billing Summary")
    print("--------------------------------")
    print(f"Hours used:    {hours:.2f} h")
    print(f"Hourly rate:   ${hourly_rate:.3f}")
    print(f"Cost so far:   ${cost:.2f}")
    print(f"Monthly cap:   ${monthly_cap:.2f}")
    if cost >= monthly_cap:
        print("⚠ You are at or above the monthly cap (further compute effectively free).")
    else:
        print(f"Remaining before cap: ${monthly_cap - cost:.2f}")


def cmd_snapshot(args: list) -> None:
    cfg = load_env()
    droplet_id = cfg["DO_DROPLET_ID"]
    name = args[0] if args else f"devctl-snapshot-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    print(f"Creating snapshot '{name}' for droplet {droplet_id}...")
    data = do_request(
        "POST",
        f"/droplets/{droplet_id}/actions",
        cfg,
        json={"type": "snapshot", "name": name},
    )
    print("Snapshot requested.")
    print(json.dumps(data, indent=2))


def cmd_logs(args: list) -> None:
    cfg = load_env()
    droplet_id = cfg["DO_DROPLET_ID"]
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


def cmd_update(args: list) -> None:
    """
    Auto-update via git pull if inside a git repo.
    """
    if not (ROOT / ".git").exists():
        print("Not a git repo. Please update manually (e.g., re-download).")
        return
    print("Running: git pull")
    try:
        subprocess.check_call(["git", "-C", str(ROOT), "pull"])
    except subprocess.CalledProcessError as e:
        print(f"git pull failed: {e}")
        sys.exit(e.returncode)


def cmd_version(args: list) -> None:
    print(read_version())


def print_help() -> None:
    print(f"devctl {read_version()}")
    print("Usage: devctl <command> [args]\n")
    print("Commands:")
    print("  dev-up        Start droplet and wait until active")
    print("  dev-down      Power off droplet")
    print("  do-bill       Estimate monthly cost from actions")
    print("  snapshot [n]  Create a snapshot with optional name")
    print("  logs          Show recent droplet actions")
    print("  update        git pull (if repo cloned)")
    print("  --version     Show version")
    print("  -h, --help    Show this help")


def main(argv: list) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print_help()
        return

    cmd = argv[0]
    args = argv[1:]

    if cmd == "dev-up":
        cmd_dev_up(args)
    elif cmd == "dev-down":
        cmd_dev_down(args)
    elif cmd == "do-bill":
        cmd_do_bill(args)
    elif cmd == "snapshot":
        cmd_snapshot(args)
    elif cmd == "logs":
        cmd_logs(args)
    elif cmd == "update":
        cmd_update(args)
    elif cmd in ("--version", "version"):
        cmd_version(args)
    else:
        print(f"Unknown command: {cmd}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
