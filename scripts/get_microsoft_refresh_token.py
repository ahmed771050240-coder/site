"""One-time Microsoft consumer OAuth device-code setup for SULTAN WALLET.

Run locally/Termux after creating a Microsoft app registration with:
- Supported account types: personal Microsoft accounts
- Public client/device code flow enabled
- Microsoft Graph delegated permission: Mail.Send
The refresh token is a secret. Copy it directly to Render environment variables;
never commit it or paste it into chat.
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request


CLIENT_ID = os.getenv("MS_CLIENT_ID", "").strip()
SCOPES = "offline_access https://graph.microsoft.com/Mail.Send"
BASE = "https://login.microsoftonline.com/consumers/oauth2/v2.0"


def post_form(url: str, data: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(details) from exc


def main() -> None:
    if not CLIENT_ID:
        raise SystemExit("Set MS_CLIENT_ID to the Application (client) ID first.")
    device = post_form(
        f"{BASE}/devicecode",
        {"client_id": CLIENT_ID, "scope": SCOPES},
    )
    print(device.get("message", "Open the Microsoft device sign-in page and enter the displayed code."))
    device_code = device["device_code"]
    interval = int(device.get("interval", 5))
    deadline = time.time() + int(device.get("expires_in", 900))
    while time.time() < deadline:
        time.sleep(interval)
        try:
            token = post_form(
                f"{BASE}/token",
                {
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                },
            )
            refresh_token = token.get("refresh_token")
            if refresh_token:
                print("\nAUTHORIZATION SUCCESSFUL")
                print("Copy this refresh token directly into Render as MS_REFRESH_TOKEN.")
                print(refresh_token)
                return
            raise SystemExit("No refresh token returned. Confirm offline_access consent.")
        except Exception as exc:
            body = str(exc)
            if "authorization_pending" in body:
                continue
            if "slow_down" in body:
                interval += 5
                continue
            if body:
                raise SystemExit(f"Microsoft authorization failed: {body}")
            raise
    raise SystemExit("Device code expired. Run the script again.")


if __name__ == "__main__":
    main()
