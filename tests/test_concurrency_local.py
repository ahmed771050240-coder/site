import runpy
import threading
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

print("Loading isolated test database...")
ns = runpy.run_path("tests/test_local_api.py")

auth_server = ns["auth_server"]
headers = ns["h"]
recipient_phone = ns["p2"]

# Fund only the temporary SQLite test accounts.
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

payload = {
    "recipient_phone": recipient_phone,
    "amount": "10.00",
    "currency": "SAR",
    "idempotency_key": "concurrent-key-0001",
    "description": "isolated concurrency test"
}

def send_request():
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
    results = list(pool.map(lambda _: send_request(), range(2)))

print("\nCONCURRENT RESPONSES:")
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
        "SELECT COUNT(*) FROM wallet_transactions WHERE idempotency_key=?",
        ("concurrent-key-0001",)
    ).fetchone()[0]

    ledger_count = auth_server.execute(
        con,
        """SELECT COUNT(*) FROM wallet_ledger
           WHERE reference IN (
               SELECT reference FROM wallet_transactions
               WHERE idempotency_key=?
           )""",
        ("concurrent-key-0001",)
    ).fetchone()[0]

print("\nDATABASE CHECK:")
print("Sender balance:", sender)
print("Receiver balance:", receiver)
print("Transaction count:", tx_count)
print("Ledger entries:", ledger_count)

if sender == 9000 and receiver == 1000 and tx_count == 1 and ledger_count == 2:
    print("\nPASS: No duplicate debit; balances and ledger are consistent.")
else:
    print("\nFAIL: Concurrency needs investigation.")
