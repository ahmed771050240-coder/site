"""Production PostgreSQL API for SULTAN WALLET.

Balances are an internal platform ledger only. No external money movement is enabled.
"""
from __future__ import annotations

import base64, hashlib, hmac, json, os, re, secrets, time, uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
WEB_APP = ROOT / "web_app" / "index.html"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
JWT_SECRET = os.getenv("JWT_SECRET", "")
CURRENCIES = ("YER", "SAR", "AED", "USD")
bearer = HTTPBearer(auto_error=True)
app = FastAPI(title="SULTAN WALLET API", version="2.0.0")


def db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=10)


def migrate():
    with db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
          version INTEGER PRIMARY KEY, applied_at BIGINT NOT NULL
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
          id BIGSERIAL PRIMARY KEY,
          phone TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          created_at BIGINT NOT NULL,
          phone_verified BOOLEAN NOT NULL DEFAULT FALSE
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS wallet_accounts (
          user_id BIGINT NOT NULL REFERENCES users(id),
          currency VARCHAR(3) NOT NULL CHECK(currency IN ('YER','SAR','AED','USD')),
          balance_minor BIGINT NOT NULL DEFAULT 0 CHECK(balance_minor >= 0),
          status TEXT NOT NULL DEFAULT 'active',
          created_at BIGINT NOT NULL,
          PRIMARY KEY(user_id,currency)
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS wallet_transactions (
          reference TEXT PRIMARY KEY,
          sender_user_id BIGINT NOT NULL REFERENCES users(id),
          receiver_user_id BIGINT NOT NULL REFERENCES users(id),
          currency VARCHAR(3) NOT NULL,
          amount_minor BIGINT NOT NULL CHECK(amount_minor > 0),
          fee_minor BIGINT NOT NULL DEFAULT 0,
          status TEXT NOT NULL,
          description TEXT,
          idempotency_key TEXT NOT NULL,
          created_at BIGINT NOT NULL,
          UNIQUE(sender_user_id,idempotency_key)
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS wallet_ledger (
          entry_id TEXT PRIMARY KEY,
          reference TEXT NOT NULL REFERENCES wallet_transactions(reference),
          user_id BIGINT NOT NULL REFERENCES users(id),
          currency VARCHAR(3) NOT NULL,
          direction TEXT NOT NULL CHECK(direction IN ('debit','credit')),
          amount_minor BIGINT NOT NULL CHECK(amount_minor > 0),
          created_at BIGINT NOT NULL
        )""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_wallet_tx_sender ON wallet_transactions(sender_user_id,created_at DESC)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_wallet_tx_receiver ON wallet_transactions(receiver_user_id,created_at DESC)")
        con.execute("INSERT INTO schema_migrations(version,applied_at) VALUES(1,%s) ON CONFLICT(version) DO NOTHING",(int(time.time()),))


def require_config():
    if len(JWT_SECRET.encode("utf-8")) < 32:
        raise HTTPException(status_code=503, detail="JWT_SECRET غير مضبوط أو أقصر من 32 بايت")
    if not DATABASE_URL:
        raise HTTPException(status_code=503, detail="DATABASE_URL غير مضبوط")


def make_token(user_id: int) -> str:
    payload = {"sub": int(user_id), "exp": int(time.time()) + 3600}
    raw = base64.urlsafe_b64encode(json.dumps(payload,separators=(",",":")).encode()).rstrip(b"=").decode()
    sig = hmac.new(JWT_SECRET.encode(),raw.encode(),hashlib.sha256).hexdigest()
    return raw + "." + sig


def read_token(token: str) -> int:
    try:
        raw,sig=token.split(".",1)
        expected=hmac.new(JWT_SECRET.encode(),raw.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig,expected): raise ValueError()
        payload=json.loads(base64.urlsafe_b64decode(raw+"="*(-len(raw)%4)))
        if int(payload["exp"]) < int(time.time()): raise ValueError()
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401,detail="جلسة الدخول غير صالحة أو انتهت")


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    return read_token(credentials.credentials)


def norm_phone(phone: str) -> str:
    value=re.sub(r"[\s()-]","",phone)
    if not re.fullmatch(r"\+?[0-9]{7,15}",value):
        raise HTTPException(status_code=400,detail="رقم الهاتف غير صالح")
    return value


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt=salt or secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,600000)
    return salt.hex()+"$"+digest.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt,digest=stored.split("$",1)
        actual=hash_password(password,bytes.fromhex(salt)).split("$",1)[1]
        return hmac.compare_digest(actual,digest)
    except Exception: return False


class Credentials(BaseModel):
    phone: str = Field(min_length=7,max_length=20)
    password: str = Field(min_length=8,max_length=128)


class LoginCredentials(BaseModel):
    phone: str = Field(min_length=7,max_length=20)
    password: str = Field(min_length=1,max_length=128)


class TransferRequest(BaseModel):
    recipient_phone: str = Field(min_length=7,max_length=20)
    amount: str = Field(min_length=1,max_length=20)
    currency: str = Field(min_length=3,max_length=3)
    idempotency_key: str = Field(min_length=8,max_length=100)
    description: str = Field(default="تحويل داخلي",max_length=200)


def minor_units(value: str) -> int:
    try:
        amount=Decimal(value)
        if not amount.is_finite() or amount<=0: raise ValueError()
        minor=amount*100
        if minor != minor.to_integral_value(): raise ValueError()
        return int(minor)
    except (InvalidOperation,ValueError):
        raise HTTPException(status_code=400,detail="المبلغ غير صالح أو يتجاوز منزلتين عشريتين")


def fmt(value: int) -> str:
    return f"{Decimal(value)/Decimal(100):.2f}"


def create_accounts(con, user_id: int):
    now=int(time.time())
    for currency in CURRENCIES:
        con.execute("""INSERT INTO wallet_accounts(user_id,currency,balance_minor,status,created_at)
        VALUES(%s,%s,0,'active',%s) ON CONFLICT(user_id,currency) DO NOTHING""",(user_id,currency,now))


@app.on_event("startup")
def startup():
    require_config()
    migrate()


@app.get("/health")
def health():
    require_config()
    try:
        with db() as con:
            row=con.execute("""SELECT
              to_regclass('public.users') AS users,
              to_regclass('public.wallet_accounts') AS accounts,
              to_regclass('public.wallet_transactions') AS tx,
              to_regclass('public.wallet_ledger') AS ledger""").fetchone()
        if not all(row.values()):
            raise HTTPException(status_code=503,detail="جداول قاعدة البيانات غير مكتملة")
        return {"status":"ok","service":"SULTAN WALLET API","database":"postgresql","real_money_enabled":False}
    except HTTPException: raise
    except Exception as exc:
        raise HTTPException(status_code=503,detail="قاعدة البيانات غير متاحة") from exc


@app.get("/app")
def web_app():
    if not WEB_APP.is_file():
        raise HTTPException(status_code=503,detail="واجهة التطبيق غير منشورة")
    return FileResponse(WEB_APP,media_type="text/html")


@app.post("/register",status_code=201)
def register(data: Credentials):
    require_config()
    phone=norm_phone(data.phone)
    try:
        with db() as con:
            row=con.execute("""INSERT INTO users(phone,password_hash,created_at)
              VALUES(%s,%s,%s) RETURNING id""",(phone,hash_password(data.password),int(time.time()))).fetchone()
            create_accounts(con,row["id"])
        return {"message":"تم إنشاء الحساب","user_id":row["id"],"phone_verified":False,
                "next_step":"يلزم ربط خدمة تحقق SMS قبل اعتماد رقم الهاتف"}
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409,detail="هذا الرقم مسجل مسبقًا")


@app.post("/login")
def login(data: LoginCredentials):
    require_config()
    phone=norm_phone(data.phone)
    with db() as con:
        user=con.execute("SELECT id,password_hash,phone_verified FROM users WHERE phone=%s",(phone,)).fetchone()
    if not user or not verify_password(data.password,user["password_hash"]):
        raise HTTPException(status_code=401,detail="رقم الهاتف أو كلمة المرور غير صحيحة")
    return {"access_token":make_token(user["id"]),"token_type":"bearer","expires_in":3600,
            "phone_verified":bool(user["phone_verified"])}


@app.get("/me")
def me(user_id: int = Depends(current_user)):
    with db() as con:
        row=con.execute("SELECT id,phone,created_at,phone_verified FROM users WHERE id=%s",(user_id,)).fetchone()
    if not row: raise HTTPException(status_code=404,detail="الحساب غير موجود")
    return row


@app.get("/wallet")
def wallet(user_id: int = Depends(current_user)):
    with db() as con:
        create_accounts(con,user_id)
        rows=con.execute("SELECT currency,balance_minor,status FROM wallet_accounts WHERE user_id=%s ORDER BY currency",(user_id,)).fetchall()
    return {"mode":"internal_wallet","real_money_enabled":False,"accounts":[{"currency":r["currency"],"balance":fmt(r["balance_minor"]),"status":r["status"]} for r in rows]}


@app.get("/wallet/transactions")
def transactions(limit: int = 30,user_id: int = Depends(current_user)):
    limit=max(1,min(limit,100))
    with db() as con:
        rows=con.execute("""SELECT reference,sender_user_id,receiver_user_id,currency,amount_minor,fee_minor,status,description,created_at
        FROM wallet_transactions WHERE sender_user_id=%s OR receiver_user_id=%s ORDER BY created_at DESC LIMIT %s""",(user_id,user_id,limit)).fetchall()
    return {"transactions":[{"reference":r["reference"],"type":"sent" if r["sender_user_id"]==user_id else "received",
      "currency":r["currency"],"amount":fmt(r["amount_minor"]),"fee":fmt(r["fee_minor"]),
      "status":r["status"],"description":r["description"],"created_at":r["created_at"]} for r in rows]}


@app.post("/wallet/transfers")
def transfer(data: TransferRequest,user_id: int = Depends(current_user)):
    currency=data.currency.upper()
    if currency not in CURRENCIES: raise HTTPException(status_code=400,detail="العملة غير مدعومة")
    amount=minor_units(data.amount)
    recipient_phone=norm_phone(data.recipient_phone)
    now=int(time.time())
    try:
        with db() as con:
            previous=con.execute("""SELECT reference,status,amount_minor,currency FROM wallet_transactions
              WHERE sender_user_id=%s AND idempotency_key=%s""",(user_id,data.idempotency_key)).fetchone()
            if previous:
                return {"reference":previous["reference"],"status":previous["status"],"amount":fmt(previous["amount_minor"]),"currency":previous["currency"],"real_money_enabled":False}
            recipient=con.execute("SELECT id FROM users WHERE phone=%s",(recipient_phone,)).fetchone()
            if not recipient: raise HTTPException(status_code=404,detail="المستلم غير موجود")
            receiver_id=recipient["id"]
            if receiver_id==user_id: raise HTTPException(status_code=400,detail="لا يمكن التحويل إلى حسابك نفسه")
            create_accounts(con,user_id); create_accounts(con,receiver_id)
            # Lock both accounts in stable order to prevent concurrent double-spend/deadlocks.
            ids=sorted([user_id,receiver_id])
            con.execute("SELECT user_id FROM wallet_accounts WHERE currency=%s AND user_id=ANY(%s) ORDER BY user_id FOR UPDATE",(currency,ids)).fetchall()
            sender=con.execute("SELECT balance_minor,status FROM wallet_accounts WHERE user_id=%s AND currency=%s",(user_id,currency)).fetchone()
            receiver=con.execute("SELECT status FROM wallet_accounts WHERE user_id=%s AND currency=%s",(receiver_id,currency)).fetchone()
            if sender["status"]!="active" or receiver["status"]!="active": raise HTTPException(status_code=403,detail="أحد الحسابات غير نشط")
            if sender["balance_minor"]<amount: raise HTTPException(status_code=400,detail="الرصيد غير كافٍ لإتمام التحويل")
            con.execute("UPDATE wallet_accounts SET balance_minor=balance_minor-%s WHERE user_id=%s AND currency=%s",(amount,user_id,currency))
            con.execute("UPDATE wallet_accounts SET balance_minor=balance_minor+%s WHERE user_id=%s AND currency=%s",(amount,receiver_id,currency))
            ref="SW-"+uuid.uuid4().hex[:20].upper()
            con.execute("""INSERT INTO wallet_transactions(reference,sender_user_id,receiver_user_id,currency,amount_minor,fee_minor,status,description,idempotency_key,created_at)
              VALUES(%s,%s,%s,%s,%s,0,'completed',%s,%s,%s)""",(ref,user_id,receiver_id,currency,amount,data.description, data.idempotency_key,now))
            con.execute("""INSERT INTO wallet_ledger(entry_id,reference,user_id,currency,direction,amount_minor,created_at)
              VALUES(%s,%s,%s,%s,'debit',%s,%s),(%s,%s,%s,%s,'credit',%s,%s)""",
              (uuid.uuid4().hex,ref,user_id,currency,amount,now,uuid.uuid4().hex,ref,receiver_id,currency,amount,now))
        return {"message":"تم تسجيل التحويل الداخلي بنجاح","reference":ref,"status":"completed","amount":fmt(amount),"currency":currency,"real_money_enabled":False}
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409,detail="مفتاح العملية مستخدم مسبقاً؛ حدّث سجل العمليات")
