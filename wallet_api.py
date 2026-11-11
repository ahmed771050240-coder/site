"""SULTAN WALLET API client.

All wallet operations are server-authoritative. This module never fabricates
balances or marks a transfer successful without a successful API response.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

API_URL = os.getenv(
    "SULTAN_WALLET_API_URL",
    "https://sultan-wallet-api.onrender.com",
).rstrip("/")
TIMEOUT_SECONDS = 15


class WalletAPIError(RuntimeError):
    pass


class WalletAPI:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or API_URL).rstrip("/")
        self.token: str | None = None

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        url = self.base_url + "/" + path.lstrip("/")
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if authenticated and self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = urllib.request.Request(
            url, data=data, headers=headers, method=method.upper()
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                raw = response.read().decode("utf-8")
                result = json.loads(raw) if raw else {}
                if not isinstance(result, dict):
                    raise WalletAPIError("استجابة الخادم غير صالحة")
                return result
        except urllib.error.HTTPError as exc:
            try:
                body = json.loads(exc.read().decode("utf-8"))
                detail = body.get("detail", body.get("message", str(exc)))
            except Exception:
                detail = str(exc)
            raise WalletAPIError(str(detail)) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise WalletAPIError(
                "تعذر الاتصال بخادم SULTAN WALLET؛ تحقق من الإنترنت وحالة الخادم."
            ) from exc
        except json.JSONDecodeError as exc:
            raise WalletAPIError("أعاد الخادم بيانات غير مفهومة") from exc

    def health(self) -> dict[str, Any]:
        return self.request("GET", "/health", authenticated=False)

    def register(self, phone: str, password: str) -> dict[str, Any]:
        return self.request(
            "POST", "/register",
            {"phone": phone, "password": password},
            authenticated=False,
        )

    def login(self, phone: str, password: str) -> dict[str, Any]:
        result = self.request(
            "POST", "/login",
            {"phone": phone, "password": password},
            authenticated=False,
        )
        token = result.get("access_token")
        if not token:
            raise WalletAPIError("لم يُرجع الخادم رمز جلسة الدخول")
        self.token = str(token)
        return result

    def me(self) -> dict[str, Any]:
        self._require_session()
        return self.request("GET", "/me")

    def wallet(self) -> dict[str, Any]:
        self._require_session()
        return self.request("GET", "/wallet")

    def transactions(self, limit: int = 50) -> dict[str, Any]:
        self._require_session()
        limit = max(1, min(int(limit), 100))
        return self.request("GET", f"/wallet/transactions?limit={limit}")

    def transfer(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._require_session()
        result = self.request("POST", "/wallet/transfers", payload)
        if result.get("status") != "completed":
            raise WalletAPIError("لم يؤكد الخادم إتمام التحويل")
        return result

    def logout(self) -> None:
        self.token = None

    def _require_session(self) -> None:
        if not self.token:
            raise WalletAPIError("سجّل الدخول أولاً")
