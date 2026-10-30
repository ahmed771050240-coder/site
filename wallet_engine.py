import re
import uuid
import time
from decimal import Decimal, InvalidOperation

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field


CURRENCIES = ("YER", "SAR", "USD")


class TransferRequest(BaseModel):
    recipient_phone: str = Field(min_length=7, max_length=20)
    amount: str = Field(min_length=1, max_length=20)
    currency: str = Field(min_length=3, max_length=3)
    idempotency_key: str = Field(min_length=8, max_length=100)
    description: str = Field(default="تحويل داخلي", max_length=200)


def register_wallet_routes(app, connect_db, execute, read_token, bearer):

    def ensure_schema():
        with connect_db() as con:
            execute(con, """
                CREATE TABLE IF NOT EXISTS wallet_accounts (
                    user_id INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    balance_minor INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at INTEGER NOT NULL,
                    PRIMARY KEY (user_id, currency)
                )
            """)

            execute(con, """
                CREATE TABLE IF NOT EXISTS wallet_transactions (
                    reference TEXT PRIMARY KEY,
                    sender_user_id INTEGER NOT NULL,
                    receiver_user_id INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    amount_minor INTEGER NOT NULL,
                    fee_minor INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    description TEXT,
                    idempotency_key TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    UNIQUE(sender_user_id, idempotency_key)
                )
            """)

            execute(con, """
                CREATE TABLE IF NOT EXISTS wallet_ledger (
                    entry_id TEXT PRIMARY KEY,
                    reference TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    amount_minor INTEGER NOT NULL,
                    created_at INTEGER NOT NULL
                )
            """)

            execute(con, """
                CREATE INDEX IF NOT EXISTS idx_wallet_transactions_sender
                ON wallet_transactions(sender_user_id, created_at)
            """)

            execute(con, """
                CREATE INDEX IF NOT EXISTS idx_wallet_transactions_receiver
                ON wallet_transactions(receiver_user_id, created_at)
            """)

    def authenticated_user(credentials: HTTPAuthorizationCredentials):
        return read_token(credentials.credentials)

    def create_accounts(con, user_id):
        now = int(time.time())
        for currency in CURRENCIES:
            execute(
                con,
                """INSERT INTO wallet_accounts
                   (user_id, currency, balance_minor, status, created_at)
                   VALUES (?, ?, 0, 'active', ?)
                   ON CONFLICT(user_id, currency) DO NOTHING""",
                (user_id, currency, now)
            )

    def parse_amount(value):
        try:
            amount = Decimal(value)
            if not amount.is_finite() or amount <= 0:
                raise ValueError()
            minor = amount * 100
            if minor != minor.to_integral_value():
                raise ValueError()
            return int(minor)
        except (InvalidOperation, ValueError):
            raise HTTPException(
                status_code=400,
                detail="المبلغ غير صالح أو يتجاوز منزلتين عشريتين"
            )

    def format_amount(value):
        return f"{Decimal(value) / Decimal(100):.2f}"

    def require_user(credentials):
        return authenticated_user(credentials)

    @app.get("/wallet")
    def wallet(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
        ensure_schema()
        user_id = require_user(credentials)

        with connect_db() as con:
            create_accounts(con, user_id)
            rows = execute(
                con,
                """SELECT currency, balance_minor, status
                   FROM wallet_accounts WHERE user_id = ?
                   ORDER BY currency""",
                (user_id,)
            ).fetchall()

        return {
            "mode": "internal_wallet",
            "real_money_enabled": False,
            "accounts": [
                {
                    "currency": row["currency"],
                    "balance": format_amount(row["balance_minor"]),
                    "status": row["status"]
                }
                for row in rows
            ]
        }

    @app.get("/wallet/transactions")
    def wallet_transactions(
        limit: int = 30,
        credentials: HTTPAuthorizationCredentials = Depends(bearer)
    ):
        ensure_schema()
        user_id = require_user(credentials)
        limit = max(1, min(limit, 100))

        with connect_db() as con:
            rows = execute(
                con,
                """SELECT reference, sender_user_id, receiver_user_id,
                          currency, amount_minor, fee_minor, status,
                          description, created_at
                   FROM wallet_transactions
                   WHERE sender_user_id = ? OR receiver_user_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (user_id, user_id, limit)
            ).fetchall()

        return {
            "transactions": [
                {
                    "reference": row["reference"],
                    "type": (
                        "sent" if row["sender_user_id"] == user_id
                        else "received"
                    ),
                    "currency": row["currency"],
                    "amount": format_amount(row["amount_minor"]),
                    "fee": format_amount(row["fee_minor"]),
                    "status": row["status"],
                    "description": row["description"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
        }

    @app.post("/wallet/transfers")
    def transfer(
        data: TransferRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer)
    ):
        ensure_schema()
        sender_id = require_user(credentials)

        currency = data.currency.upper()
        if currency not in CURRENCIES:
            raise HTTPException(status_code=400, detail="العملة غير مدعومة")

        amount_minor = parse_amount(data.amount)
        recipient_phone = re.sub(r"\s+", "", data.recipient_phone)

        if not re.fullmatch(r"\+?[0-9]{7,15}", recipient_phone):
            raise HTTPException(status_code=400, detail="رقم المستلم غير صالح")

        now = int(time.time())
        reference = "SW-" + uuid.uuid4().hex[:20].upper()

        with connect_db() as con:
            previous = execute(
                con,
                """SELECT reference, status, amount_minor, currency
                   FROM wallet_transactions
                   WHERE sender_user_id = ? AND idempotency_key = ?""",
                (sender_id, data.idempotency_key)
            ).fetchone()

            if previous:
                return {
                    "message": "هذه العملية سبق تسجيلها",
                    "reference": previous["reference"],
                    "status": previous["status"],
                    "amount": format_amount(previous["amount_minor"]),
                    "currency": previous["currency"]
                }

            recipient = execute(
                con,
                "SELECT id FROM users WHERE phone = ?",
                (recipient_phone,)
            ).fetchone()

            if not recipient:
                raise HTTPException(status_code=404, detail="المستلم غير موجود")

            receiver_id = recipient["id"]

            if sender_id == receiver_id:
                raise HTTPException(
                    status_code=400,
                    detail="لا يمكن التحويل إلى حسابك نفسه"
                )

            create_accounts(con, sender_id)
            create_accounts(con, receiver_id)

            sender_account = execute(
                con,
                """SELECT balance_minor, status FROM wallet_accounts
                   WHERE user_id = ? AND currency = ?""",
                (sender_id, currency)
            ).fetchone()

            receiver_account = execute(
                con,
                """SELECT status FROM wallet_accounts
                   WHERE user_id = ? AND currency = ?""",
                (receiver_id, currency)
            ).fetchone()

            if sender_account["status"] != "active" or receiver_account["status"] != "active":
                raise HTTPException(status_code=403, detail="أحد الحسابات غير نشط")

            debit = execute(
                con,
                """UPDATE wallet_accounts
                   SET balance_minor = balance_minor - ?
                   WHERE user_id = ? AND currency = ?
                   AND balance_minor >= ? AND status = 'active'""",
                (amount_minor, sender_id, currency, amount_minor)
            )

            if debit.rowcount != 1:
                raise HTTPException(
                    status_code=400,
                    detail="الرصيد غير كافٍ لإتمام التحويل"
                )

            execute(
                con,
                """UPDATE wallet_accounts
                   SET balance_minor = balance_minor + ?
                   WHERE user_id = ? AND currency = ?""",
                (amount_minor, receiver_id, currency)
            )

            execute(
                con,
                """INSERT INTO wallet_transactions
                   (reference, sender_user_id, receiver_user_id,
                    currency, amount_minor, fee_minor, status,
                    description, idempotency_key, created_at)
                   VALUES (?, ?, ?, ?, ?, 0, 'completed', ?, ?, ?)""",
                (
                    reference, sender_id, receiver_id, currency,
                    amount_minor, data.description,
                    data.idempotency_key, now
                )
            )

            execute(
                con,
                """INSERT INTO wallet_ledger
                   (entry_id, reference, user_id, currency,
                    direction, amount_minor, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    uuid.uuid4().hex, reference, sender_id,
                    currency, "debit", amount_minor, now
                )
            )

            execute(
                con,
                """INSERT INTO wallet_ledger
                   (entry_id, reference, user_id, currency,
                    direction, amount_minor, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    uuid.uuid4().hex, reference, receiver_id,
                    currency, "credit", amount_minor, now
                )
            )

        return {
            "message": "تم تسجيل التحويل الداخلي بنجاح",
            "reference": reference,
            "status": "completed",
            "amount": format_amount(amount_minor),
            "currency": currency,
            "real_money_enabled": False
        }
