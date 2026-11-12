"""SULTAN WALLET API starter.

This API intentionally exposes no deposit, withdrawal, transfer, card-issuing,
or service-purchase endpoint. Those flows require a licensed provider adapter,
verified webhooks, reconciliation, and production security review.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import jwt
import psycopg
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

DATABASE_URL = os.getenv("DATABASE_URL", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = "HS256"
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "30"))
CURRENCIES = ("SAR", "USD", "AED", "YER")
password_hasher = PasswordHasher()
bearer = HTTPBearer(auto_error=False)

app = FastAPI(
    title="SULTAN WALLET API",
    version="1.0.0",
    description="Authentication and read-only wallet foundation. Money movement is disabled.",
)


def db_connection():
    if not DATABASE_URL:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return psycopg.connect(DATABASE_URL)


def require_security_config() -> None:
    if len(JWT_SECRET_KEY) < 32:
        raise HTTPException(status_code=503, detail="JWT_SECRET_KEY must be configured with at least 32 characters")


class RegisterRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=24, pattern=r"^[+0-9][0-9 -]{5,22}$")
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=12, max_length=256)


class LoginRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=24)
    password: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def issue_token(user_id: int) -> str:
    require_security_config()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=TOKEN_MINUTES)},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    require_security_config()
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    with db_connection() as conn:
        row = conn.execute(
            "SELECT id, phone, full_name, status FROM app_users WHERE id = %s",
            (user_id,),
        ).fetchone()
    if row is None or row[3] != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account unavailable")
    return {"id": row[0], "phone": row[1], "full_name": row[2], "status": row[3]}


@app.get("/health")
def health():
    return {"status": "ok", "money_movement_enabled": False}


@app.post("/auth/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest):
    require_security_config()
    password_hash = password_hasher.hash(body.password)
    try:
        with db_connection() as conn:
            row = conn.execute(
                """INSERT INTO app_users(phone, full_name, password_hash)
                   VALUES (%s, %s, %s) RETURNING id""",
                (body.phone.strip(), body.full_name.strip(), password_hash),
            ).fetchone()
            user_id = row[0]
            conn.executemany(
                "INSERT INTO wallet_accounts(user_id, currency) VALUES (%s, %s)",
                [(user_id, currency) for currency in CURRENCIES],
            )
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Phone number already registered")
    token = issue_token(user_id)
    return TokenResponse(access_token=token, expires_in=TOKEN_MINUTES * 60)


@app.post("/auth/login", response_model=TokenResponse)
def login(body: LoginRequest):
    require_security_config()
    with db_connection() as conn:
        row = conn.execute(
            "SELECT id, password_hash, status FROM app_users WHERE phone = %s",
            (body.phone.strip(),),
        ).fetchone()
    if row is None or row[2] != "active":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        password_hasher.verify(row[1], body.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if password_hasher.check_needs_rehash(row[1]):
        with db_connection() as conn:
            conn.execute(
                "UPDATE app_users SET password_hash = %s WHERE id = %s",
                (password_hasher.hash(body.password), row[0]),
            )
    return TokenResponse(access_token=issue_token(row[0]), expires_in=TOKEN_MINUTES * 60)


@app.get("/me")
def me(user: dict = Depends(current_user)):
    return user


@app.get("/wallets")
def wallets(user: dict = Depends(current_user)):
    with db_connection() as conn:
        rows = conn.execute(
            """SELECT currency, balance, status
               FROM wallet_accounts WHERE user_id = %s ORDER BY
               CASE currency WHEN 'SAR' THEN 1 WHEN 'USD' THEN 2
                             WHEN 'AED' THEN 3 WHEN 'YER' THEN 4 ELSE 5 END""",
            (user["id"],),
        ).fetchall()
    return {
        "real_money_enabled": False,
        "wallets": [
            {"currency": row[0], "balance": str(Decimal(row[1])), "status": row[2]}
            for row in rows
        ],
    }


@app.get("/capabilities")
def capabilities():
    return {
        "authentication": True,
        "wallet_read": True,
        "kyc_review": False,
        "deposits": False,
        "withdrawals": False,
        "transfers": False,
        "card_issuing": False,
        "service_fulfillment": False,
        "note": "Enable money features only after licensed provider integration and independent security review.",
    }


# Email verification (Microsoft Graph OAuth2; secrets live only in Render env vars)
import hashlib
import hmac
import re
import secrets
from datetime import timedelta
from backend.email_service import send_verification_email


class EmailCodeRequest(BaseModel):
    email: str = Field(min_length=6, max_length=254)


class EmailCodeVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^[0-9]{6}$")


def _email_code_digest(user_id: int, email: str, code: str) -> str:
    material = f"{JWT_SECRET_KEY}:{user_id}:{email.lower()}:{code}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


@app.post("/auth/email/request-code")
def request_email_code(body: EmailCodeRequest, user: dict = Depends(current_user)):
    require_security_config()
    email = body.email.strip().lower()
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\\.[A-Za-z0-9-]+)+", email):
        raise HTTPException(status_code=422, detail="Invalid email address")
    with db_connection() as conn:
        recent = conn.execute(
            """SELECT count(*) FROM email_verification_codes
               WHERE user_id = %s AND created_at > now() - interval '1 hour'""",
            (user["id"],),
        ).fetchone()[0]
        if recent >= 3:
            raise HTTPException(status_code=429, detail="Too many codes requested; try again later")
        conn.execute(
            "UPDATE app_users SET email = %s, email_verified = FALSE WHERE id = %s",
            (email, user["id"]),
        )
        conn.execute(
            """UPDATE email_verification_codes SET consumed_at = now()
               WHERE user_id = %s AND consumed_at IS NULL""",
            (user["id"],),
        )
        code = f"{secrets.randbelow(1_000_000):06d}"
        conn.execute(
            """INSERT INTO email_verification_codes
               (user_id, email, code_hash, expires_at)
               VALUES (%s, %s, %s, now() + interval '10 minutes')""",
            (user["id"], email, _email_code_digest(user["id"], email, code)),
        )
    try:
        send_verification_email(email, code)
    except RuntimeError as exc:
        # Do not expose OAuth tokens, provider responses, or account credentials.
        raise HTTPException(status_code=503, detail="Email delivery is not configured or failed") from exc
    return {"status": "sent", "email": email, "expires_in": 600}


@app.post("/auth/email/verify-code")
def verify_email_code(body: EmailCodeVerifyRequest, user: dict = Depends(current_user)):
    require_security_config()
    with db_connection() as conn:
        row = conn.execute(
            """SELECT id, email, code_hash, expires_at, attempts, consumed_at
               FROM email_verification_codes
               WHERE user_id = %s ORDER BY id DESC LIMIT 1 FOR UPDATE""",
            (user["id"],),
        ).fetchone()
        if row is None or row[5] is not None:
            raise HTTPException(status_code=400, detail="No active verification code")
        if row[4] >= 5:
            raise HTTPException(status_code=429, detail="Too many incorrect attempts")
        if row[3] <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Verification code expired")
        expected = _email_code_digest(user["id"], row[1], body.code)
        if not hmac.compare_digest(row[2], expected):
            conn.execute(
                "UPDATE email_verification_codes SET attempts = attempts + 1 WHERE id = %s",
                (row[0],),
            )
            raise HTTPException(status_code=400, detail="Incorrect verification code")
        conn.execute(
            "UPDATE email_verification_codes SET consumed_at = now() WHERE id = %s",
            (row[0],),
        )
        conn.execute(
            "UPDATE app_users SET email_verified = TRUE WHERE id = %s AND email = %s",
            (user["id"], row[1]),
        )
    return {"status": "verified", "email_verified": True}


@app.get("/auth/email/status")
def email_verification_status(user: dict = Depends(current_user)):
    with db_connection() as conn:
        row = conn.execute(
            "SELECT email, email_verified FROM app_users WHERE id = %s",
            (user["id"],),
        ).fetchone()
    return {"email": row[0], "email_verified": bool(row[1])}
