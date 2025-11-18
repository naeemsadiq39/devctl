from pathlib import Path

def write_ssh_config(ip: str, cfg: dict):
    ssh_user = cfg["DEVCTL_SSH_USER"]
    ssh_key = cfg["DEVCTL_SSH_KEY"]

    home = Path.home()
    ssh_dir = home / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)

    config_file = ssh_dir / "config"

    block = (
        "Host devctl\n"
        f"    HostName {ip}\n"
        f"    User {ssh_user}\n"
        f"    IdentityFile {ssh_dir / ssh_key}\n"
    )

    existing = config_file.read_text() if config_file.exists() else ""
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

    new_lines.extend(block.rstrip("\n").splitlines())

    config_file.write_text("\n".join(new_lines) + "\n")
    print(f"Updated SSH config: {config_file}")
