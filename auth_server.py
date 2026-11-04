import os
import re
import json
import hmac
import time
import base64
import hashlib
import secrets
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent
DB = BASE / "wallet_auth.db"
SECRET_FILE = BASE / "auth_secret.key"

if not SECRET_FILE.exists():
    fd = os.open(str(SECRET_FILE), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(secrets.token_bytes(32))

SECRET = SECRET_FILE.read_bytes()
app = FastAPI(title="SULTAN WALLET Account API", version="1.0")
bearer = HTTPBearer()


def connect_db():
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row
    return con


with connect_db() as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            phone_verified INTEGER NOT NULL DEFAULT 0
        )
    """)


def normalize_phone(phone):
    return re.sub(r"[\s()-]", "", phone)


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 600000
    )
    return salt.hex() + "$" + digest.hex()


def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        actual = hash_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
        return hmac.compare_digest(actual, digest_hex)
    except (ValueError, TypeError):
        return False


def make_token(user_id):
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + 3600
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    signature = hmac.new(SECRET, encoded.encode(), hashlib.sha256).hexdigest()
    return encoded + "." + signature


def read_token(token):
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(
            SECRET, encoded.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError()
        raw = base64.urlsafe_b64decode(
            encoded + "=" * (-len(encoded) % 4)
        )
        payload = json.loads(raw)
        if int(payload["exp"]) < int(time.time()):
            raise ValueError()
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="جلسة الدخول غير صالحة أو انتهت")


class RegisterRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=1, max_length=128)


@app.get("/health")
def health():
    return {"status": "ok", "service": "SULTAN WALLET Account API"}


@app.post("/register", status_code=201)
def register(data: RegisterRequest):
    phone = normalize_phone(data.phone)
    if not re.fullmatch(r"\+?[0-9]{7,15}", phone):
        raise HTTPException(status_code=400, detail="رقم الهاتف غير صالح")

    with connect_db() as con:
        try:
            cur = con.execute(
                "INSERT INTO users(phone, password_hash, created_at) VALUES (?, ?, ?)",
                (phone, hash_password(data.password), int(time.time()))
            )
            user_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="هذا الرقم مسجل مسبقًا")

    return {
        "message": "تم إنشاء الحساب",
        "user_id": user_id,
        "phone_verified": False,
        "next_step": "يلزم ربط خدمة تحقق SMS قبل اعتماد رقم الهاتف"
    }


@app.post("/login")
def login(data: LoginRequest):
    phone = normalize_phone(data.phone)
    with connect_db() as con:
        user = con.execute(
            "SELECT id, password_hash, phone_verified FROM users WHERE phone = ?",
            (phone,)
        ).fetchone()

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="رقم الهاتف أو كلمة المرور غير صحيحة")

    return {
        "access_token": make_token(user["id"]),
        "token_type": "bearer",
        "expires_in": 3600,
        "phone_verified": bool(user["phone_verified"]),
        "message": "تم التحقق من كلمة المرور"
    }


@app.get("/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    user_id = read_token(credentials.credentials)
    with connect_db() as con:
        user = con.execute(
            "SELECT id, phone, created_at, phone_verified FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="الحساب غير موجود")

    return dict(user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
