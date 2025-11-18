from pathlib import Path
import sys
import subprocess

from .env import load_env
from .commands import cmd_dev_up, cmd_dev_down, cmd_snapshot, cmd_logs, cmd_update, cmd_do_bill
from .config import cmd_config
from .ssh_keys import ssh_list, ssh_add, ssh_delete, ssh_sync, ssh_attach, ssh_login

ROOT = Path(__file__).resolve().parents[3]
VERSION_FILE = ROOT / "VERSION"

def read_version():
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "0.0.0-dev"

def print_help():
    print(f"devctl {read_version()}")
    print("Commands:")
    print("  dev-up")
    print("  dev-down")
    print("  do-bill")
    print("  snapshot [name]")
    print("  logs")
    print("  update")
    print("  config        Configure droplets + SSH key")

    print("  ssh        ")
    print("      ssh list       List DigitalOcean SSH keys")
    print("      ssh add <pub>  Upload SSH public key to DO")
    print("      ssh delete     Remove a DO SSH key")
    print("      ssh sync       Ensure .env SSH key exists in DO")
    print("      ssh attach     Add local SSH key to droplet (authorized_keys)")
    print("      ssh login      SSH into droplet directly")




    print("  --version")

def main(argv):
    if not argv:
        print_help()
        return

    cmd = argv[0]
    args = argv[1:]

    if cmd == "dev-up":
        cmd_dev_up(args)
    elif cmd == "dev-down":
        cmd_dev_down(args)
    elif cmd == "do-bill":
        cmd_do_bill()
    elif cmd == "snapshot":
        cmd_snapshot(args)
    elif cmd == "logs":
        cmd_logs(args)
    elif cmd == "update":
        cmd_update(args)
    elif cmd == "config":
        cmd_config()
    elif cmd in ("--version", "version"):
        print(read_version())
    elif cmd == "ssh":
        if not args:
            print("SSH commands: list | add | delete | sync | attach | login")
            return

        sub = args[0]
        rest = args[1:]

        if sub == "list":
            ssh_list()
        elif sub == "add":
            ssh_add(rest)
        elif sub == "delete":
            ssh_delete(rest)
        elif sub == "sync":
            ssh_sync(rest)
        elif sub == "attach":
            ssh_attach(rest)
        elif sub == "login":
            ssh_login(rest)
        else:
            print("Unknown ssh command:", sub)


    else:
        print_help()
