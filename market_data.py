"""Market data adapters for SULTAN WALLET.

FX reference rates are daily mid-market observations from Frankfurter
(central-bank and institutional sources). Gold is an indicative XAU/USD
spot observation from XAUS. Neither feed is an executable trading quote.
"""
import time
from datetime import datetime, timezone

import requests

FX_URL = "https://api.frankfurter.dev/v2/rate/usd/{quote}"
GOLD_URL = "https://xaus.com/api/v1/spot?compact=1"
TIMEOUT = 12
_cache = {}
_cache_at = {}


def _cached(key, ttl, loader):
    now = time.time()
    if key in _cache and now - _cache_at.get(key, 0) < ttl:
        return _cache[key]
    value = loader()
    _cache[key] = value
    _cache_at[key] = now
    return value


def _fetch_fx():
    rates = {}
    observations = {}
    for quote in ("SAR", "AED", "YER"):
        try:
            response = requests.get(FX_URL.format(quote=quote.lower()), timeout=TIMEOUT)
            response.raise_for_status()
            item = response.json()
            rates[quote] = item["rate"]
            observations[quote] = item.get("date")
        except (requests.RequestException, ValueError, KeyError, TypeError):
            # Never substitute an estimated or hard-coded exchange rate.
            rates[quote] = None
            observations[quote] = None
    return {
        "base": "USD",
        "rates": rates,
        "observations": observations,
        "source": "Frankfurter (blended institutional reference rates)",
        "source_url": "https://frankfurter.dev/",
        "kind": "daily_reference_mid_rate",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "note": "أسعار مرجعية يومية وليست أسعار تنفيذ أو أسعار السوق المحلية.",
    }


def get_fx():
    return _cached("fx", 300, _fetch_fx)


def _fetch_gold():
    response = requests.get(GOLD_URL, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    state = data.get("data_state") or {}
    price = data.get("spot_usd_oz")
    if price is None:
        xau = data.get("xau") or {}
        price = xau.get("price")
    if price is None:
        raise ValueError("Gold provider did not return a spot price")
    return {
        "symbol": "XAU",
        "price": float(price),
        "currency": "USD",
        "unit": "troy_ounce",
        "source": "XAUS",
        "source_url": "https://xaus.com/",
        "status": state.get("status", "unknown"),
        "as_of": state.get("as_of") or data.get("updated_at"),
        "age_seconds": state.get("age_seconds"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "note": "سعر الذهب الفوري الاسترشادي بالدولار للأونصة الترويسية، وليس عرض بيع مضموناً.",
    }


def get_gold():
    return _cached("gold", 60, _fetch_gold)
