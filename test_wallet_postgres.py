import os
from urllib.parse import urlparse
import asyncio
import secrets

import httpx
import psycopg
from psycopg.rows import dict_row

# يجب ضبط DATABASE_URL قبل تشغيل هذا الملف
if not os.environ.get("DATABASE_URL"):
    raise SystemExit("ERROR: DATABASE_URL is required")


DB_URL = os.environ["DATABASE_URL"]
_db = urlparse(DB_URL)

if _db.hostname not in ("localhost", "127.0.0.1"):
    raise SystemExit("BLOCKED: PostgreSQL tests require localhost")

if _db.path.lstrip("/") != "sultan_wallet_test":
    raise SystemExit("BLOCKED: database must be sultan_wallet_test")

import auth_server
BASE_URL = "http://test"
transport = httpx.ASGITransport(
    app=auth_server.app,
    raise_app_exceptions=False
)

async def main():
    async with httpx.AsyncClient(
        transport=transport,
        base_url=BASE_URL,
        timeout=30
    ) as client:

        suffix = str(secrets.randbelow(900000) + 100000)
        phone1 = "967771" + suffix
        phone2 = "967772" + suffix
        password = "TestPass123!"

        print("1. REGISTER USERS")
        r1 = await client.post("/register", json={
            "phone": phone1, "password": password
        })
        r2 = await client.post("/register", json={
            "phone": phone2, "password": password
        })
        assert r1.status_code == 201, r1.text
        assert r2.status_code == 201, r2.text
        sender_id = r1.json()["user_id"]
        receiver_id = r2.json()["user_id"]
        print("PASS: users registered")

        print("2. LOGIN")
        l1 = await client.post("/login", json={
            "phone": phone1, "password": password
        })
        l2 = await client.post("/login", json={
            "phone": phone2, "password": password
        })
        assert l1.status_code == 200, l1.text
        assert l2.status_code == 200, l2.text

        h1 = {"Authorization": "Bearer " + l1.json()["access_token"]}
        h2 = {"Authorization": "Bearer " + l2.json()["access_token"]}

        print("3. CREATE WALLETS")
        w1 = await client.get("/wallet", headers=h1)
        w2 = await client.get("/wallet", headers=h2)
        assert w1.status_code == 200, w1.text
        assert w2.status_code == 200, w2.text
        assert len(w1.json()["accounts"]) == 4
        assert w1.json()["real_money_enabled"] is False
        print("PASS: YER, SAR, AED, USD")

        print("4. FUND ISOLATED TEST ACCOUNT")
        with psycopg.connect(DB_URL) as con:
            con.execute("""
                UPDATE wallet_accounts
                SET balance_minor = 100000
                WHERE user_id = %s AND currency = 'SAR'
            """, (sender_id,))

        print("5. INTERNAL TRANSFER")
        payload = {
            "recipient_phone": phone2,
            "amount": "10.00",
            "currency": "SAR",
            "idempotency_key": "pg-basic-" + secrets.token_hex(8),
            "description": "PostgreSQL integration test"
        }
        transfer = await client.post(
            "/wallet/transfers", json=payload, headers=h1
        )
        assert transfer.status_code == 200, transfer.text
        reference = transfer.json()["reference"]
        print("PASS:", reference)

        print("6. IDEMPOTENCY")
        replay = await client.post(
            "/wallet/transfers", json=payload, headers=h1
        )
        assert replay.status_code == 200, replay.text
        assert replay.json()["reference"] == reference

        changed = dict(payload)
        changed["amount"] = "11.00"
        conflict = await client.post(
            "/wallet/transfers", json=changed, headers=h1
        )
        assert conflict.status_code == 409, conflict.text
        print("PASS: duplicate and changed requests handled")

        print("7. INSUFFICIENT BALANCE")
        poor = dict(payload)
        poor["amount"] = "999999.00"
        poor["idempotency_key"] = "pg-poor-" + secrets.token_hex(8)
        insufficient = await client.post(
            "/wallet/transfers", json=poor, headers=h1
        )
        assert insufficient.status_code == 400, insufficient.text

        print("8. NEGATIVE AMOUNT")
        negative = dict(payload)
        negative["amount"] = "-1.00"
        negative["idempotency_key"] = "pg-negative-" + secrets.token_hex(8)
        bad = await client.post(
            "/wallet/transfers", json=negative, headers=h1
        )
        assert bad.status_code == 400, bad.text

        print("9. CONCURRENT IDENTICAL TRANSFERS")
        concurrent_payload = dict(payload)
        concurrent_payload["amount"] = "5.00"
        concurrent_payload["idempotency_key"] = (
            "pg-concurrent-" + secrets.token_hex(8)
        )

        results = await asyncio.gather(*[
            client.post(
                "/wallet/transfers",
                json=concurrent_payload,
                headers=h1
            )
            for _ in range(10)
        ])
        assert all(r.status_code == 200 for r in results), [
            (r.status_code, r.text) for r in results
        ]
        refs = {r.json()["reference"] for r in results}
        assert len(refs) == 1, refs

        with psycopg.connect(DB_URL, row_factory=dict_row) as con:
            count = con.execute("""
                SELECT COUNT(*) AS n FROM wallet_transactions
                WHERE sender_user_id = %s AND idempotency_key = %s
            """, (sender_id, concurrent_payload["idempotency_key"])).fetchone()["n"]
            assert count == 1, count
        print("PASS: 10 requests produced one transaction")

        print("10. ROLLBACK ON LEDGER FAILURE")
        with psycopg.connect(DB_URL) as con:
            before = con.execute("""
                SELECT user_id, balance_minor
                FROM wallet_accounts
                WHERE user_id IN (%s, %s) AND currency = 'SAR'
                ORDER BY user_id
            """, (sender_id, receiver_id)).fetchall()

            before_counts = con.execute("""
                SELECT
                    (SELECT COUNT(*) FROM wallet_transactions),
                    (SELECT COUNT(*) FROM wallet_ledger),
                    (SELECT COUNT(*) FROM wallet_audit_log)
            """).fetchone()

            con.execute("""
                CREATE OR REPLACE FUNCTION sultan_test_fail_ledger()
                RETURNS trigger AS $$
                BEGIN
                    RAISE EXCEPTION 'TEST_INJECTED_LEDGER_FAILURE';
                END;
                $$ LANGUAGE plpgsql
            """)
            con.execute("""
                CREATE TRIGGER sultan_test_ledger_failure
                BEFORE INSERT ON wallet_ledger
                FOR EACH ROW EXECUTE FUNCTION sultan_test_fail_ledger()
            """)

        rollback_payload = dict(payload)
        rollback_payload["amount"] = "7.00"
        rollback_payload["idempotency_key"] = (
            "pg-rollback-" + secrets.token_hex(8)
        )
        failed = await client.post(
            "/wallet/transfers",
            json=rollback_payload,
            headers=h1
        )
        assert failed.status_code == 500, (
            failed.status_code, failed.text
        )

        with psycopg.connect(DB_URL) as con:
            after = con.execute("""
                SELECT user_id, balance_minor
                FROM wallet_accounts
                WHERE user_id IN (%s, %s) AND currency = 'SAR'
                ORDER BY user_id
            """, (sender_id, receiver_id)).fetchall()

            after_counts = con.execute("""
                SELECT
                    (SELECT COUNT(*) FROM wallet_transactions),
                    (SELECT COUNT(*) FROM wallet_ledger),
                    (SELECT COUNT(*) FROM wallet_audit_log)
            """).fetchone()

            assert before == after, (before, after)
            assert before_counts == after_counts, (
                before_counts, after_counts
            )

            con.execute("""
                DROP TRIGGER sultan_test_ledger_failure ON wallet_ledger
            """)
            con.execute("DROP FUNCTION sultan_test_fail_ledger()")

        print("PASS: failed transfer fully rolled back")

        print("11. FINAL ACCOUNTING RECONCILIATION")
        with psycopg.connect(DB_URL) as con:
            sums = con.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN direction='debit'
                        THEN amount_minor ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN direction='credit'
                        THEN amount_minor ELSE 0 END), 0)
                FROM wallet_ledger
                WHERE currency = 'SAR'
            """).fetchone()
            assert sums[0] == sums[1], sums
        print("PASS: ledger debits equal credits")

        print("\nALL POSTGRESQL TESTS PASSED")

asyncio.run(main())
