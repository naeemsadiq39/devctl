import requests
import sys
import time
from datetime import datetime
from .env import load_env

def do_request(method: str, path: str, cfg: dict, **kwargs):
    url = cfg["DO_API_BASE"].rstrip("/") + path
    headers = {
        "Authorization": f"Bearer {cfg['DO_TOKEN']}",
        "Content-Type": "application/json"
    }

    resp = requests.request(method, url, headers=headers, **kwargs)
    if not resp.ok:
        print(f"[ERROR] {method} {url} -> {resp.status_code}")
        try:
            print(resp.json())
        except:
            print(resp.text)
        sys.exit(1)

    if not resp.text.strip():
        return {}

    return resp.json()

def wait_for_active(cfg: dict, droplet_id: str, timeout_sec=300):
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

def tag_droplet(cfg, droplet_id: str, tag_name: str):
    """
    Create tag if missing, then attach droplet.
    """
    # Step 1: create tag (safe even if it already exists)
    create_body = {"name": tag_name}

    print(f"Ensuring tag '{tag_name}' exists...")
    do_request("POST", "/tags", cfg, json=create_body)

    # Step 2: attach droplet to tag
    body = {
        "resources": [
            {"resource_id": str(droplet_id), "resource_type": "droplet"}
        ]
    }

    print(f"Applying tag '{tag_name}' to droplet {droplet_id}...")
    return do_request("POST", f"/tags/{tag_name}/resources", cfg, json=body)

def get_droplet_ip(cfg, droplet_id: str):
    data = do_request("GET", f"/droplets/{droplet_id}", cfg)
    nets = data["droplet"]["networks"]["v4"]
    for n in nets:
        if n["type"] == "public":
            return n["ip_address"]
    raise RuntimeError("Droplet has no public IP")
