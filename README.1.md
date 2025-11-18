y
# devctl

> [!CAUTION]
> This is an early WIP tool intended for personal use.
> A stable release is coming soon — until then, **review code before running commands**, especially anything involving SSH or cloud resources.

`devctl` is a cross-platform command-line tool for managing **cloud development environments**.
Currently focused on **DigitalOcean**, with support for:

- Droplet lifecycle management
- Billing estimation
- Full SSH key workflow
- Automatic SSH config generation
- Droplet tagging
- Interactive setup wizard
- Complete compatibility across **Windows, Linux, and macOS**

It is designed to be ultra-lightweight and require **no installation** or pip packages:
just unzip and run `devctl` from any terminal.

---

# 🚀 Features

## ☁️ Droplet Lifecycle (DigitalOcean)
- `devctl dev-up` — start a droplet, wait until ready, auto-write SSH config
- `devctl dev-down` — safely power off a droplet
- `devctl snapshot` — create snapshots
- `devctl logs` — view recent droplet actions
- Automatic rebuild of `~/.ssh/config` for `Host devctl`

## 💸 Billing Tools
- `devctl do-bill` — estimate hourly usage + monthly projected cost
- Based on actual DO `power_on` / `power_off` events
- Supports custom hourly rate + monthly cap
- Helpful for disposable dev environments

## 🔐 SSH Key Management (Local + DigitalOcean)
- `devctl ssh list` — list DO account SSH keys
- `devctl ssh add <pub>` — upload a key to DO
- `devctl ssh delete` — interactive delete
- `devctl ssh sync` — ensure your `.env` key exists in DO
- `devctl ssh attach` — write key to droplet `authorized_keys`
- `devctl ssh login` — SSH into droplet via configured key

## ⚙️ Setup & Config (Interactive)
- `devctl config`:
  - Detect local SSH keys
  - Let you select one
  - Fetch DO droplets
  - Choose one
  - Apply DO tag (`devctl`)
  - Generate `.env`
  - Create SSH config entry

## 🔄 Self Updates
- `devctl update` performs `git pull` if run from a repo.

## 🧩 Cross-Platform
✔ Windows CMD
✔ Windows PowerShell
✔ Git Bash / MSYS2
✔ Linux
✔ macOS

---

# 📦 Installation

Download the release ZIP from:

👉 https://github.com/<YOUR_USER>/devctl/releases

And extract anywhere, for example:

```

C:\devctl
~/devctl/

````

### Windows Installation

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
cd C:\devctl
.\install-devctl.ps1
````

### Linux/macOS Installation

```bash
cd ~/devctl
sudo ./install.sh
```

Verify:

```bash
devctl --version
```

---

# 🧰 Initial Setup

1. Create a `.env` from the template:

```
cp .env.example .env
```

2. Add your DigitalOcean API token:

```
DO_TOKEN=your_token_here
```

3. Run the guided setup:

```bash
devctl config
```

This will:

✔ Detect local SSH keys
✔ Let you choose one
✔ Detect DO droplets
✔ Let you choose one
✔ Tag droplet as `devctl`
✔ Save config to `.env`

---

# 🛠 Commands

## Core Commands

```bash
devctl dev-up        # Start droplet, wait until active
devctl dev-down      # Power off droplet
devctl do-bill       # Estimate monthly cost
devctl snapshot      # Create snapshot
devctl logs          # Show last DO droplet actions
devctl config        # Interactive first-time setup
devctl update        # git pull (if in repo)
devctl --version     # Show version
devctl -h            # Help
```

---

## 🔐 SSH Commands

```bash
devctl ssh list       # List DigitalOcean SSH keys
devctl ssh add <pub>  # Upload SSH key to DO
devctl ssh delete     # Remove a DO SSH key
devctl ssh sync       # Ensure .env key exists on DO
devctl ssh attach     # Add local key to droplet
devctl ssh login      # SSH login using configured key
```

Example:

```bash
devctl ssh login
```

Equivalent to:

```bash
ssh root@<droplet-ip> -i ~/.ssh/<configured-key>
```

---

# 🏷 Droplet Tagging

`devctl config` ensures:

* DO tag `devctl` exists
* Selected droplet receives the tag

This lets you filter or bulk-manage devctl droplets from the DO Dashboard.

---

# 🗂 Environment Variables

Saved in `.env`:

```
DO_TOKEN=...
DEVCTL_DROPLET_ID=123456
DEVCTL_SSH_KEY=~/.ssh/id_rsa
DEVCTL_SSH_USER=root
DO_API_BASE=https://api.digitalocean.com/v2
DEVCTL_WRITE_SSH_CONFIG=true
```

> **Note**: Environment variables override `.env`.

---

# 📁 Project Structure

```
devctl/
│   devctl
│   devctl.bat
│   .env.example
│   VERSION
│   install.sh
│   install-devctl.ps1
│
├── scripts/
│   ├── python/
│   │   ├── devctl_core.py
│   │   └── pjq.py
│   ├── bash/
│   ├── bat/
│   └── ps1/
│
└── env/
    └── dev.env
```

---

# 🏛 Architecture

```
+--------------------------+
|        devctl CLI        |
|  (bash/cmd/ps1 wrappers) |
+-------------+------------+
              |
              v
+--------------------------+
|     Python Core Engine    |
|   scripts/python/devctl   |
+-------------+-------------+
              |
              v
+--------------------------+
|   DigitalOcean REST API   |
|  droplets, SSH keys, logs |
+--------------------------+
```

All real logic lives in the Python core, ensuring **consistent behavior** across every OS/shell.

---

# 📚 Roadmap

* ☁️ Multi-cloud support

  * AWS Lightsail
  * Vultr
  * Linode
  * UpCloud

* 🔒 Automatic idle shutdown timers

* 🧵 Multiple project profiles

* 📦 Droplet auto-provisioning

* 🙋 devctl agent for real-time billing and SSH events

* 🧰 VSCode extension

* 🖥 Dashboard / TUI mode

* 🌐 Add DigitalOcean Spaces helpers (sync, backup)

---

# 🤝 Contributing

Contributions welcome!

Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit a pull request

You can also file issues for:

* Feature requests
* Bug reports
* Documentation improvements
* OS-specific issues

---

# 🔐 Security

> **Important:**
>
> * Never commit `.env` with API tokens.
> * Use read-only API tokens where possible.
> * Always verify SSH keys before attaching them.
> * Review actions before running scripts on production droplets.

The repository includes a `.gitignore` to prevent accidental leakage of secrets.

If you find a security issue, **do not open a public GitHub issue**.
Please email: **<YOUR_EMAIL>**.

---

# 📝 Versioning

devctl follows **semantic versioning**:

```
MAJOR.MINOR.PATCH
```

Example:

```
0.1.0
```

Version is stored in:

```
VERSION
```

---

# 🧪 Testing

Manual commands:

```bash
python scripts/python/devctl_core.py dev-up
python scripts/python/devctl_core.py do-bill
python scripts/python/devctl_core.py ssh list
```

Automated test suite coming soon.

---

# 📸 Screenshots (optional)

*(You can add these later)*

```
[devctl showing droplet boot sequence]
[billing estimator output]
[config wizard]
```

---

# 📜 License

MIT — see [`LICENSE`](LICENSE) for details.

---

<p align="center">Made with 🔧 and ⚡</p>
```

---

# 🚀 Want me to generate matching files?

I can also generate:

✅ `CONTRIBUTING.md`
✅ `SECURITY.md`
✅ `.gitattributes`
✅ Issue templates
✅ Pull Request templates
✅ A beautiful SVG logo
✅ Changelog system

Just say:

**“generate the rest”**
