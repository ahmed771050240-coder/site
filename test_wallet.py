import os, wallet_engine as we, market_data as md
DB="/tmp/test_sultan.db"
if os.path.exists(DB): os.remove(DB)
we.init_db(DB)
import sqlite3; con=sqlite3.connect(DB); con.execute("INSERT INTO users (phone,pwd_hash,full_name) VALUES (?,?,?)",("777000001","x","Ali")); con.execute("INSERT INTO users (phone,pwd_hash,full_name) VALUES (?,?,?)",("777000002","x","Sara")); con.commit(); con.close()
we.deposit(DB,1,1000,"SAR")
assert we.get_balance(DB,1,"SAR")==1000
r=we.transfer(DB,1,2,"777000002",200,"SAR","internal",idempotency_key="k1")
assert we.get_balance(DB,1,"SAR")==800 and we.get_balance(DB,2,"SAR")==200
print("ALL TESTS PASSED")
