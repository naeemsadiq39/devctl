
# devctl

> [!CAUTION]
> This is a WIP for personal usage, I expect to finalise a release in the coming weeks. until then double check the code before running it.

`devctl` is a cross-platform command-line tool for managing cloud development
instances.
It currently focuses on **DigitalOcean**, with support for:

- Droplet power management
- Billing estimation
- Automatic SSH configuration
- Tagging droplets
- SSH key upload / attach / login
- Full Windows + Linux + macOS compatibility

It is designed to be ultra-lightweight and require **no installation**:
just unzip and run `devctl` from any terminal.

---

## 🚀 Features

### ☁️ Droplet Lifecycle
- `devctl dev-up`: Start a droplet and wait until it's active
- `devctl dev-down`: Power off a droplet
- `devctl snapshot`: Create snapshots
- `devctl logs`: View recent droplet actions
- Automatic SSH config generation (`Host devctl`)

### 💸 Billing Tools
- `devctl do-bill`: Estimate hourly usage and projected monthly cost
- Uses power_on/power_off actions for accuracy
- Supports custom hourly pricing and monthly caps

### 🔐 SSH Key Management (local + DigitalOcean)
- `devctl ssh list`: List SSH keys stored in DigitalOcean
- `devctl ssh add <pubkey>`: Upload a local key to DO
- `devctl ssh delete`: Delete DO keys interactively
- `devctl ssh sync`: Ensure `.env` key exists in DO
- `devctl ssh attach`: Add a local public key to the droplet
- `devctl ssh login`: Open an SSH session into the droplet

### ⚙️ Setup & Config
- `devctl config`:
  - Select SSH key from `~/.ssh`
  - Select droplet from DigitalOcean
  - Auto-create and apply DO tag (`devctl`)
  - Write `.env` with all required settings

### 🔄 Updates
- `devctl update`: Auto-pull updates if in a Git repo

---

## 📦 Installation

Download the release ZIP and extract anywhere:

```

devctl/
├── devctl           # shell launcher (Linux/macOS)
├── devctl.bat       # Windows launcher
├── scripts/
│   ├── python/
│   ├── bash/
│   ├── bat/
│   ├── ps1/
└── .env.example

```

No pip install, no requirements — it works out of the box.

---

## 🧰 Initial Setup

1. Add your DigitalOcean API token to `.env` or set it manually:

```

DO_TOKEN=yourtoken

```

2. Run:

```

devctl config

````

This will:

✔ Detect your SSH keys
✔ Let you choose one
✔ Fetch your droplets
✔ Let you choose one
✔ Tag the droplet (`devctl`)
✔ Save everything into `.env`

---

## 🛠 Commands

### Core Commands

```bash
devctl dev-up        # start droplet, wait until ready
devctl dev-down      # power off droplet
devctl do-bill       # estimate monthly cost
devctl snapshot       # take snapshot
devctl logs           # show droplet actions
devctl update         # git pull (if in repo)
devctl config         # configure droplet + SSH key
devctl --version      # show version
````

---

## 🔐 SSH Commands

```bash
devctl ssh list       # list DigitalOcean SSH keys
devctl ssh add <pub>  # upload SSH public key to DO
devctl ssh delete     # remove DO SSH key
devctl ssh sync       # ensure .env key is uploaded
devctl ssh attach     # add local pubkey to droplet (authorized_keys)
devctl ssh login      # SSH into droplet using configured key
```

**Login example:**

```bash
devctl ssh login
```

Equivalent to:

```
ssh root@<droplet-ip> -i ~/.ssh/<yourkey>
```

---

## 🏷 Droplet Tagging

`devctl config` automatically:

* Ensures a DigitalOcean tag named `devctl` exists
* Applies it to your selected droplet

You can use this in the DO dashboard to filter your dev instances.

---

## 🗂 Environment Variables

Stored in `.env`:

```
DO_TOKEN=...
DEVCTL_DROPLET_ID=...
DEVCTL_SSH_KEY=...
DEVCTL_SSH_USER=root
DO_API_BASE=https://api.digitalocean.com/v2
DEVCTL_WRITE_SSH_CONFIG=true
```

Environment variables override `.env`.

---

## 🤝 Cross-Platform Support

| Platform           | Supported | Notes                         |
| ------------------ | --------- | ----------------------------- |
| Windows CMD        | ✅         | devctl.bat                    |
| Windows PowerShell | ✅         | ps1 scripts included          |
| Git Bash / MSYS2   | ✅         | POSIX shell versions included |
| Linux (all)        | ✅         |                               |
| macOS              | ✅         |                               |

---

## 📚 Roadmap

* Multi-cloud provider support (AWS Lightsail, Vultr, Linode)
* Automatic droplet creation from templates
* Scheduled auto-shutdown / cost-limiting
* Project-based multiple instance support
* devctl agent for live SSH/billing events

---
