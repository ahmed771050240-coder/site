"""Microsoft Graph mail delivery for SULTAN WALLET.

Requires delegated Microsoft Graph Mail.Send consent and a refresh token.
Secrets are read only from the server environment, never from the APK or Git.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


def send_verification_email(recipient: str, code: str) -> None:
    client_id = os.getenv("MS_CLIENT_ID", "").strip()
    refresh_token = os.getenv("MS_REFRESH_TOKEN", "").strip()
    client_secret = os.getenv("MS_CLIENT_SECRET", "").strip()
    sender = os.getenv("SULTAN_EMAIL_FROM", "sultanwallet@outlook.sa").strip()

    if not client_id or not refresh_token:
        raise RuntimeError("Microsoft Graph mail is not configured")

    form = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "https://graph.microsoft.com/Mail.Send offline_access",
    }
    if client_secret:
        form["client_secret"] = client_secret

    token_request = urllib.request.Request(
        "https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
        data=urllib.parse.urlencode(form).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(token_request, timeout=20) as response:
            token_data = json.loads(response.read().decode("utf-8"))
        access_token = token_data["access_token"]
    except Exception as exc:
        raise RuntimeError("Microsoft OAuth token refresh failed") from exc

    message = {
        "message": {
            "subject": "رمز التحقق من SULTAN WALLET",
            "body": {
                "contentType": "Text",
                "content": (
                    f"رمز التحقق الخاص بك هو: {code}\n"
                    "صلاحية الرمز 10 دقائق. لا تشاركه مع أي شخص.\n"
                    "إذا لم تطلب هذا الرمز فتجاهل الرسالة."
                ),
            },
            "toRecipients": [{"emailAddress": {"address": recipient}}],
        },
        "saveToSentItems": True,
    }
    if sender:
        # The signed-in Microsoft mailbox is the sender. This value is informational
        # until the alias is confirmed as a permitted send-as address by Microsoft.
        message["message"]["replyTo"] = [{"emailAddress": {"address": sender}}]

    send_request = urllib.request.Request(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        data=json.dumps(message).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(send_request, timeout=20) as response:
            if response.status != 202:
                raise RuntimeError(f"Microsoft Graph returned HTTP {response.status}")
    except Exception as exc:
        raise RuntimeError("Microsoft Graph could not send the verification email") from exc
