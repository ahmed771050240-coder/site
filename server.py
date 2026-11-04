from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import hashlib
from datetime import datetime

app = FastAPI(title="Sultan Wallet Backend", version="2.0")

def init_db():
    conn = sqlite3.connect("sultan_wallet.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            amount REAL,
            type TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TransferRequest(BaseModel):
    sender: str
    receiver: str
    amount: float

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/register")
def register(user: UserRegister):
    conn = sqlite3.connect("sultan_wallet.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, balance, created_at) VALUES (?, ?, ?, ?)",
            (user.username, hash_password(user.password), 100.0, datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="اسم المستخدم موجود مسبقاً.")
    conn.close()
    return {"status": "success", "message": "تم إنشاء الحساب بنجاح وإضافة رصيد ترحيبي!"}

@app.post("/login")
def login(user: UserLogin):
    conn = sqlite3.connect("sultan_wallet.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, balance FROM users WHERE username = ? AND password_hash = ?",
        (user.username, hash_password(user.password))
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="خطأ في اسم المستخدم أو كلمة المرور.")
    return {"status": "success", "username": row[0], "balance": row[1]}

@app.post("/transfer")
def transfer(req: TransferRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="المبلغ غير صالح للتحويل.")
    
    conn = sqlite3.connect("sultan_wallet.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username = ?", (req.sender,))
    sender_row = cursor.fetchone()
    if not sender_row or sender_row[0] < req.amount:
        conn.close()
        raise HTTPException(status_code=400, detail="عذراً، رصيدك غير كافي.")
        
    cursor.execute("SELECT balance FROM users WHERE username = ?", (req.receiver,))
    receiver_row = cursor.fetchone()
    if not receiver_row:
        conn.close()
        raise HTTPException(status_code=404, detail="المستلم غير موجود.")

    cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (req.amount, req.sender))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (req.amount, req.receiver))
    cursor.execute(
        "INSERT INTO transactions (sender, receiver, amount, type, timestamp) VALUES (?, ?, ?, ?, ?)",
        (req.sender, req.receiver, req.amount, "TRANSFER", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"تم تحويل {req.amount} بنجاح إلى {req.receiver}"}
