"""Small HTTPS client for the SULTAN WALLET API. No financial state is stored here."""
from __future__ import annotations

import json
import urllib.error
import urllib.request


class WalletAPIError(Exception):
    """A safe, user-displayable API error."""


class WalletAPI:
    def __init__(self, base_url: str, opener=None, timeout: float = 12.0):
        if not base_url.startswith("https://") and not base_url.startswith("http://127.0.0.1"):
            raise ValueError("API URL must use HTTPS")
        self.base_url = base_url.rstrip("/")
        self.opener = opener or urllib.request.urlopen
        self.timeout = timeout

    def _request(self, method: str, path: str, payload=None, token=None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = "Bearer " + token
        req = urllib.request.Request(self.base_url + path, data=body, headers=headers, method=method)
        try:
            with self.opener(req, timeout=self.timeout) as response:
                raw = response.read()
            result = json.loads(raw.decode("utf-8")) if raw else {}
            if not isinstance(result, dict):
                raise WalletAPIError("استجابة الخادم غير صالحة")
            return result
        except urllib.error.HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("detail", "تعذر تنفيذ الطلب")
            except Exception:
                detail = "تعذر تنفيذ الطلب"
            raise WalletAPIError(str(detail)) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise WalletAPIError("الخادم غير متاح حالياً؛ تحقق من الاتصال وحاول لاحقاً") from None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise WalletAPIError("استجابة الخادم غير مفهومة") from None

    def register(self, phone: str, full_name: str, password: str):
        return self._request("POST", "/auth/register", {
            "phone": phone.strip(), "full_name": full_name.strip(), "password": password
        })

    def login(self, phone: str, password: str):
        return self._request("POST", "/auth/login", {
            "phone": phone.strip(), "password": password
        })

    def me(self, token: str):
        return self._request("GET", "/me", token=token)

    def wallets(self, token: str):
        return self._request("GET", "/wallets", token=token)
