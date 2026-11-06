import sys, types, os, tempfile
# Local SQLite integration tests; psycopg is not needed on this test path.
pg = types.ModuleType('psycopg')
pg.connect = lambda *a, **k: None
pg.errors = types.SimpleNamespace(UniqueViolation=type('UniqueViolation',(Exception,),{}))
rows = types.ModuleType('psycopg.rows'); rows.dict_row = object()
sys.modules['psycopg'] = pg; sys.modules['psycopg.rows'] = rows
os.environ['AUTH_SECRET'] = 'test-secret-' + ('x'*40)
import auth_server
from pathlib import Path
from fastapi.testclient import TestClient
# Isolate every run so rerunning tests never reuses a previous test account.
auth_server.DB = Path(tempfile.mkdtemp()) / 'test_wallet_auth.db'
auth_server.init_db()
c=TestClient(auth_server.app)
health=c.get('/health'); assert health.status_code==200 and health.json()['database_connected'] is True
p1='+967777123456'; p2='+967777654321'; pw='SecurePass123'
r=c.post('/register',json={'phone':p1,'password':pw}); assert r.status_code==201,r.text
assert c.post('/register',json={'phone':p1,'password':pw}).status_code==409
assert c.post('/register',json={'phone':p2,'password':pw}).status_code==201
bad=c.post('/login',json={'phone':p1,'password':'wrongpass'}); assert bad.status_code==401
login=c.post('/login',json={'phone':p1,'password':pw}); assert login.status_code==200,login.text
token=login.json()['access_token']; h={'Authorization':'Bearer '+token}
me=c.get('/me',headers=h); assert me.status_code==200,me.text
w=c.get('/wallet',headers=h); assert w.status_code==200,w.text
assert {a['currency'] for a in w.json()['accounts']}=={'YER','SAR','AED','USD'}
# No funded balance: transfer must be rejected, no fake funds.
r=c.post('/wallet/transfers',headers=h,json={'recipient_phone':p2,'amount':'1.00','currency':'YER','idempotency_key':'test-key-0001','description':'test'})
assert r.status_code==400 and 'الرصيد غير كافٍ' in r.text,r.text
assert c.get('/wallet/transactions',headers=h).json()['transactions']==[]

# Fund test accounts directly in the isolated test database (test fixture only).
with auth_server.connect_db() as con:
    auth_server.execute(con, "UPDATE wallet_accounts SET balance_minor=25000 WHERE user_id=? AND currency='SAR'", (1,))
    auth_server.execute(con, "UPDATE wallet_accounts SET balance_minor=0 WHERE user_id=? AND currency='SAR'", (2,))
transfer_payload={'recipient_phone':p2,'amount':'50.00','currency':'SAR','idempotency_key':'transfer-key-0001','description':'integration test'}
completed=c.post('/wallet/transfers',headers=h,json=transfer_payload)
assert completed.status_code==200,completed.text
transfer_result=completed.json(); assert transfer_result['status']=='completed' and transfer_result['real_money_enabled'] is False
# Retry of the exact same request must return the same reference, without a second debit.
replayed=c.post('/wallet/transfers',headers=h,json=transfer_payload)
assert replayed.status_code==200 and replayed.json()['reference']==transfer_result['reference'],replayed.text
# Reusing an idempotency key for another recipient/amount must be rejected.
changed=dict(transfer_payload); changed['amount']='60.00'
conflict=c.post('/wallet/transfers',headers=h,json=changed)
assert conflict.status_code==409,conflict.text
with auth_server.connect_db() as con:
    sender_balance=auth_server.execute(con, "SELECT balance_minor FROM wallet_accounts WHERE user_id=1 AND currency='SAR'").fetchone()[0]
    receiver_balance=auth_server.execute(con, "SELECT balance_minor FROM wallet_accounts WHERE user_id=2 AND currency='SAR'").fetchone()[0]
    ledger_count=auth_server.execute(con, "SELECT COUNT(*) FROM wallet_ledger WHERE reference=?", (transfer_result['reference'],)).fetchone()[0]
assert (sender_balance,receiver_balance,ledger_count)==(20000,5000,2),(sender_balance,receiver_balance,ledger_count)
assert any(t['reference']==transfer_result['reference'] and t['type']=='sent' for t in c.get('/wallet/transactions',headers=h).json()['transactions'])
login2=c.post('/login',json={'phone':p2,'password':pw}); h2={'Authorization':'Bearer '+login2.json()['access_token']}
assert any(t['reference']==transfer_result['reference'] and t['type']=='received' for t in c.get('/wallet/transactions',headers=h2).json()['transactions'])
print('PASS: funded internal transfer, exact retry idempotency, conflicting-key rejection, double-entry ledger, sender/receiver history')
# Invalid precision/currency rejected before any balance mutation.
r=c.post('/wallet/transfers',headers=h,json={'recipient_phone':p2,'amount':'1.001','currency':'YER','idempotency_key':'test-key-0002','description':'test'})
assert r.status_code==400,r.text
print('PASS: health, registration, duplicate protection, login, wrong-password rejection, authenticated profile, four currency accounts, insufficient-funds protection, transaction history, decimal validation')

# Readiness must fail closed when the configured database cannot be reached.
_original_connect_db = auth_server.connect_db
def _database_down():
    raise RuntimeError('simulated database outage')
auth_server.connect_db = _database_down
unhealthy = c.get('/health')
assert unhealthy.status_code == 503, unhealthy.text
auth_server.connect_db = _original_connect_db
print('PASS: readiness endpoint returns 503 when database is unavailable')
