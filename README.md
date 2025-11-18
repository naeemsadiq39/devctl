<p align="center">

<!-- <pre>
   ____             _ _
  |  _ \  _____   _(_) |_
  | | | |/ _ \ \ / / | __|
  | |_| |  __/\ V /| | |_
  |____/ \___| \_/ |_|\__|

          devctl

</pre> -->

  <!-- <img src="./assets/logo.svg" width="full" align="center" /> -->
</p>

<h1 align="center">devctl</h1>

<p align="center">
  <strong>Cross-platform developer automation toolkit</strong>
  <br />
  Start/stop cloud dev servers, estimate billing, snapshot machines, manage SSH config, and more — all from one CLI.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue" />
  <img src="https://img.shields.io/badge/language-Python%203.9%2B-orange" />
  <img src="https://img.shields.io/badge/shell-bash%20%7C%20powershell%20%7C%20cmd-green" />
  <img src="https://img.shields.io/github/license/<YOUR_GITHUB>/devctl" />
  <img src="https://img.shields.io/github/v/release/<YOUR_GITHUB>/devctl" />
</p>

---

> [!CAUTION]
> This is an early WIP tool intended for personal use.
> A stable release is coming soon — until then, **review code before running commands**, especially anything involving SSH or cloud resources.

## 🚀 Overview

**devctl** is a portable, cross-shell CLI for managing cloud-based developer environments.
It works seamlessly across:

- **Windows CMD**
- **PowerShell**
- **Git Bash**
- **Linux**
- **macOS**

All commands funnel into a single Python core for consistency and reliability.

Use devctl to:

- 🚀 **Spin up** your disposable dev server (`devctl dev-up`)
- 🛑 **Shut it down** when you’re done (`devctl dev-down`)
- 💰 **Track usage & cost** based on DigitalOcean actions (`devctl do-bill`)
- 📸 **Snapshot** your development server (`devctl snapshot`)
- 📜 **View logs** of recent actions (`devctl logs`)
- 🔄 **Update yourself** if running inside a git clone (`devctl update`)
- 📦 **Use a single config file (.env)** for secrets and settings

Perfect for developers who want **temporary cloud dev machines** without leaving droplets running all day.

---

# ✨ Features

### 🧩 Cross-platform launchers
Works in **CMD**, **PowerShell**, **Bash**, **Git Bash**, **WSL**, and **Linux/macOS** shells.

### 🧠 Single Python core
All real logic lives in one file:
```

scripts/python/devctl_core.py

```
This keeps behavior consistent on all systems.

### 🔐 One `.env` file for credentials
Supports `.env` and `env/dev.env`.

### 🔧 Automatic SSH config
Adds/updates:

```

Host devctl
HostName <droplet-ip>
User <user>
Port <port>

```

### 💵 Billing estimator
Reads DigitalOcean `power_on` and `power_off` events to compute hourly usage and monthly rollups.

### 📸 Snapshots
Quick snapshots of your dev machine with:
```

devctl snapshot my-backup

```

### 📜 Droplet logs
Show recent DO actions:
```

devctl logs

```

### 🔄 Self-update
If installed from a Git clone:
```

devctl update

```

---

# 📦 Installation

## 📥 Download
Download the latest release:

👉 https://github.com/<YOUR_GITHUB>/devctl/releases

Extract anywhere you want and proceed with install.

---

## 🪟 **Windows Installation**

### 1. Extract the ZIP
Example:
```

C:\devctl\

````

### 2. Run the installer
From PowerShell:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
cd C:\devctl
.\install-devctl.ps1
````

### 3. Test:

```powershell
devctl --version
```

---

## 🐧 **Linux/macOS Installation**

### 1. Extract the ZIP

Example:

```
~/devctl/
```

### 2. Install:

```bash
cd ~/devctl
sudo ./install.sh
```

### 3. Test:

```bash
devctl --version
```

---

# 🔧 Configuration

Copy the sample env:

```
cp .env.example env/dev.env
```

Edit:

```dotenv
DO_TOKEN=your_digitalocean_token
DO_DROPLET_ID=123456789
DO_API_BASE=https://api.digitalocean.com/v2
DEVCTL_WRITE_SSH_CONFIG=true
DEVCTL_SSH_USER=ubuntu
DEVCTL_SSH_PORT=22
```

---

# 🕹️ Usage

## 🚀 Start the development server

```bash
devctl dev-up
```

Outputs:

```
Starting droplet 530961251...
Waiting for droplet to become active...
Status: active
Droplet IP: 143.42.55.122
Updated SSH config at ~/.ssh/config
```

---

## 🛑 Stop the server

```bash
devctl dev-down
```

---

## 💰 View estimated billing

```bash
devctl do-bill
```

Example output:

```
📊 DigitalOcean Billing Summary
--------------------------------
Hours used:    12.75 h
Hourly rate:   $0.071
Cost so far:   $0.91
Remaining before cap: $47.09
```

---

## 📸 Create snapshot

```bash
devctl snapshot my-backup
```

---

## 📜 View droplet action logs

```bash
devctl logs
```

---

## 🔄 Update devctl (if git clone)

```bash
devctl update
```

---

## 🧩 All Commands

```
devctl dev-up        Start droplet and wait until active
devctl dev-down      Power off droplet
devctl do-bill       Estimate monthly cost from actions
devctl snapshot [n]  Create snapshot with optional name
devctl logs          Show recent droplet actions
devctl update        git pull (if repo cloned)
devctl --version     Show version
devctl -h, --help    Show help
```

---

# 🧱 Project Structure

```
devctl/
│   devctl
│   devctl.bat
│   install.sh
│   install-devctl.ps1
│   .env.example
│   VERSION
│
├───bin/
│       dev-up
│       dev-down
│       do-bill
│       load-env
│
├───env/
│       dev.env
│
├───scripts/
│   ├───python/
│   │       devctl_core.py
│   │       pjq.py
│   │
│   ├───bash/
│   │       dev-up.sh
│   │       dev-down.sh
│   │       do-bill.sh
│   │       load-env.sh
│   │
│   ├───bat/
│   │       dev-up.bat
│   │       dev-down.bat
│   │       do-bill.cmd
│   │       load-env.cmd
│   │
│   └───ps1/
│           dev-up.ps1
│           dev-down.ps1
│           do-bill.ps1
│           load-env.ps1
```

---

# 🧪 Development

Clone the repo:

```bash
git clone https://github.com/<YOUR_GITHUB>/devctl.git
cd devctl
```

Run directly:

```bash
python scripts/python/devctl_core.py dev-up
```

---

# 🧵 Contributing

Pull requests welcome!
Please open issues for:

* Feature requests
* Bug reports
* Improvements to shell wrappers
* New cloud providers (AWS Lightsail, Linode, Vultr, etc.)

---

# 📜 License

[MIT](LICENSE)

---

# 🏁 Roadmap

* Multi-cloud provider support
* Auto-schedule shutdown timers
* Integrated TUI dashboard
* Docker container mode
* VSCode extension
* devctl daemon for idle shutdown
* Firebase / Supabase / DB provisioning helpers

---

<p align="center">
  <strong>Happy coding! 🚀</strong>
</p>
