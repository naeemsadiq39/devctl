from datetime import datetime, timezone
from .env import load_env
from .api import do_request


def calculate_billing():
    cfg = load_env()

    droplet_id = cfg["DEVCTL_DROPLET_ID"]  # <- corrected key name
    hourly_rate = float(cfg.get("DEVCTL_RATE", "0.071"))
    monthly_cap = float(cfg.get("DEVCTL_CAP", "48"))

    print("Fetching droplet actions...")
    actions = []
    page = 1

    while True:
        data = do_request(
            "GET",
            f"/droplets/{droplet_id}/actions?per_page=200&page={page}",
            cfg
        )
        batch = data.get("actions", [])
        if not batch:
            break

        actions.extend(batch)

        if "next" not in data.get("links", {}).get("pages", {}):
            break

        page += 1

    # Sort actions
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

        # Power ON → begin timing
        if atype == "power_on" and status == "completed":
            current_start = completed or started

        # Power OFF → stop timing
        elif atype == "power_off" and status == "completed" and current_start:
            end_time = completed or started
            if end_time:
                total_seconds += (end_time - current_start).total_seconds()
            current_start = None

    # If the droplet is still on right now
    if current_start:
        now = datetime.now(timezone.utc)
        total_seconds += (now - current_start).total_seconds()

    hours = total_seconds / 3600
    cost = hours * hourly_rate

    print("\n📊 DigitalOcean Billing Summary")
    print("--------------------------------")
    print(f"Hours used:    {hours:.2f} h")
    print(f"Hourly rate:   ${hourly_rate:.3f}")
    print(f"Cost so far:   ${cost:.2f}")
    print(f"Monthly cap:   ${monthly_cap:.2f}")

    if cost >= monthly_cap:
        print("⚠ You are at or above the monthly cap.")
    else:
        print(f"Remaining before cap: ${monthly_cap - cost:.2f}")
