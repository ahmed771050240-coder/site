import runpy
import threading
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

print("Loading isolated SQLite test database...")
ns = runpy.run_path("tests/test_local_api.py")

auth_server = ns["auth_server"]
headers = ns["h"]
recipient_phone = ns["p2"]

# Test-only funding: sender gets 100 SAR, receiver gets zero.
with auth_server.connect_db() as con:
    auth_server.execute(
        con,
        "UPDATE wallet_accounts SET balance_minor=10000 WHERE user_id=1 AND currency='SAR'"
    )
    auth_server.execute(
        con,
        "UPDATE wallet_accounts SET balance_minor=0 WHERE user_id=2 AND currency='SAR'"
    )

barrier = threading.Barrier(2)

def transfer(key):
    payload = {
        "recipient_phone": recipient_phone,
        "amount": "70.00",
        "currency": "SAR",
        "idempotency_key": key,
        "description": "competing transfer test"
    }
    try:
        with TestClient(auth_server.app) as client:
            barrier.wait(timeout=10)
            response = client.post(
                "/wallet/transfers",
                headers=headers,
                json=payload
            )
            return response.status_code, response.json()
    except Exception as exc:
        return "EXCEPTION", repr(exc)

with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(
        transfer,
        ["compete-key-0001", "compete-key-0002"]
    ))

print("\nRESPONSES:")
for result in results:
    print(result)

with auth_server.connect_db() as con:
    sender = auth_server.execute(
        con,
        "SELECT balance_minor FROM wallet_accounts WHERE user_id=1 AND currency='SAR'"
    ).fetchone()[0]

    receiver = auth_server.execute(
        con,
        "SELECT balance_minor FROM wallet_accounts WHERE user_id=2 AND currency='SAR'"
    ).fetchone()[0]

    tx_count = auth_server.execute(
        con,
        """SELECT COUNT(*) FROM wallet_transactions
           WHERE sender_user_id=1 AND currency='SAR'
           AND idempotency_key IN (?, ?)""",
        ("compete-key-0001", "compete-key-0002")
    ).fetchone()[0]

    ledger_count = auth_server.execute(
        con,
        """SELECT COUNT(*) FROM wallet_ledger
           WHERE reference IN (
               SELECT reference FROM wallet_transactions
               WHERE sender_user_id=1
               AND idempotency_key IN (?, ?)
           )""",
        ("compete-key-0001", "compete-key-0002")
    ).fetchone()[0]

print("\nBALANCE CHECK:")
print("Sender:", sender)
print("Receiver:", receiver)
print("Transactions:", tx_count)
print("Ledger entries:", ledger_count)

statuses = sorted(str(item[0]) for item in results)

if (
    statuses == ["200", "400"]
    and sender == 3000
    and receiver == 7000
    and tx_count == 1
    and ledger_count == 2
):
    print("\nPASS: Only one transfer succeeded; no overspending.")
else:
    print("\nFAIL: Competing transfer test needs investigation.")
