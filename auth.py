import hashlib, secrets, sqlite3, datetime
try:
    import bcrypt
    def hash_pwd(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
    def verify_pwd(p,h):
        try: return bcrypt.checkpw(p.encode(), h.encode())
        except: return hashlib.sha256(p.encode()).hexdigest()==h
except ImportError:
    def hash_pwd(p):
        s=secrets.token_hex(16); return s+"$"+hashlib.sha256((s+p).encode()).hexdigest()
    def verify_pwd(p,h):
        try: s,o=h.split("$"); return hashlib.sha256((s+p).encode()).hexdigest()==o
        except: return False
def create_session(db, user_id, device="android"):
    token=secrets.token_hex(32); con=sqlite3.connect(db); con.execute("INSERT INTO sessions (user_id,token,device,expires_at) VALUES (?,?,?,datetime('now','+7 days'))",(user_id,token,device)); con.commit(); con.close(); return token
