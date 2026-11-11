import json
import unittest
from unittest.mock import patch
from wallet_api import WalletAPI, WalletAPIError


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.payload


class WalletAPITests(unittest.TestCase):
    def test_register_uses_backend_contract(self):
        seen = {}
        def opener(req, timeout):
            seen["url"] = req.full_url
            seen["method"] = req.method
            seen["body"] = json.loads(req.data)
            return FakeResponse({"access_token": "token"})
        result = WalletAPI("https://api.example.test", opener).register("+967777777777", "Test User", "long-password")
        self.assertEqual(result["access_token"], "token")
        self.assertEqual(seen["url"], "https://api.example.test/auth/register")
        self.assertEqual(seen["method"], "POST")
        self.assertEqual(seen["body"]["full_name"], "Test User")

    def test_login_and_authorized_wallet_request(self):
        calls = []
        def opener(req, timeout):
            calls.append(req)
            if req.full_url.endswith("/auth/login"):
                return FakeResponse({"access_token": "abc"})
            return FakeResponse({"wallets": [{"currency": "SAR", "balance": "0.00"}]})
        api = WalletAPI("https://api.example.test", opener)
        token = api.login("123456789", "password")["access_token"]
        wallets = api.wallets(token)
        self.assertEqual(wallets["wallets"][0]["currency"], "SAR")
        self.assertEqual(calls[1].get_header("Authorization"), "Bearer abc")

    def test_rejects_insecure_remote_url(self):
        with self.assertRaises(ValueError):
            WalletAPI("http://api.example.test")

    def test_maps_http_error_without_leaking_details(self):
        import urllib.error
        def opener(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)
        with self.assertRaises(WalletAPIError):
            WalletAPI("https://api.example.test", opener).me("bad-token")


if __name__ == "__main__":
    unittest.main()
