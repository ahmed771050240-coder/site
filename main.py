# SULTAN WALLET V4.1 - BANK - CRASH FIX
import flet as ft
import sqlite3, hashlib, secrets, json, urllib.request, datetime, os, sys

CURRENCIES=["YER","SAR","USD","AED"]
RATES_FALLBACK={"YER":1.0,"SAR":0.00066,"USD":0.0025,"AED":0.0092}
GOVS=["صنعاء","عدن","تعز","حضرموت","الحديدة","إب","ذمار","مأرب","الجوف","شبوة","أبين","لحج","الضالع","البيضاء","حجة","صعدة","المحويت","عمران","ريمة","المهرة","سقطرى"]
COUNTRIES=["اليمن","السعودية","الإمارات","قطر","الكويت","عمان","البحرين","الأردن","مصر","السودان","أخرى"]

SERVICES={
 "شحن جوال - اليمن": [{"name":"يمن موبايل 1000","price":1000,"cur":"YER","code":"YM-1000"},{"name":"سبأفون 1000","price":1000,"cur":"YER","code":"SABA-1000"},{"name":"MTN 1000","price":1000,"cur":"YER","code":"MTN-1000"},{"name":"YOU 1000","price":1000,"cur":"YER","code":"YOU-1000"}],
 "شحن جوال - السعودية": [{"name":"STC سوا 50","price":50,"cur":"SAR","code":"STC-50"},{"name":"موبايلي 30","price":30,"cur":"SAR","code":"MOB-30"},{"name":"زين السعودية 50","price":50,"cur":"SAR","code":"ZAIN-SA-50"}],
 "شحن جوال - الإمارات": [{"name":"Etisalat 50","price":50,"cur":"AED","code":"ETI-50"},{"name":"du 50","price":50,"cur":"AED","code":"DU-50"}],
 "شحن جوال - مصر": [{"name":"Vodafone مصر","price":50,"cur":"USD","code":"VOD-EG-50"},{"name":"Orange مصر","price":50,"cur":"USD","code":"ORG-EG-50"}],
 "شحن جوال - دول أخرى": [{"name":"Zain الكويت","price":5,"cur":"USD","code":"ZAIN-KW-5"},{"name":"Ooredoo قطر","price":5,"cur":"USD","code":"OOR-QA-5"},{"name":"Omantel عمان","price":5,"cur":"USD","code":"OMAN-5"}],
 "ألعاب وشحن عملات": [{"name":"PUBG 60 شدة","price":0.99,"cur":"USD","code":"PUBG-60"},{"name":"PUBG 660 شدة","price":9.99,"cur":"USD","code":"PUBG-660"},{"name":"Free Fire 1060 جوهرة","price":9.99,"cur":"USD","code":"FF-1060"},{"name":"TikTok 700 كوين","price":9.99,"cur":"USD","code":"TT-700"},{"name":"Roblox 400","price":4.99,"cur":"USD","code":"RB-400"}],
 "بطاقات واشتراكات": [{"name":"Google Play 10$","price":10,"cur":"USD","code":"GP-10"},{"name":"Apple 10$","price":10,"cur":"USD","code":"AP-10"},{"name":"Netflix شهر","price":9.99,"cur":"USD","code":"NF-1M"},{"name":"Shahid VIP","price":8.99,"cur":"USD","code":"SH-1M"},{"name":"ChatGPT Plus","price":20,"cur":"USD","code":"GPT-1M"}],
}

DB_PATH = None

def get_db_path():
    global DB_PATH
    if DB_PATH: return DB_PATH
    # حاول مجلدات قابلة للكتابة في أندرويد
    for p in [os.path.expanduser("~"), "/data/data/com.sultan.wallet/files", "/storage/emulated/0/Download", "."]:
        try:
            test = os.path.join(p, "test_write.tmp")
            with open(test, "w") as f: f.write("1")
            os.remove(test)
            DB_PATH = os.path.join(p, "sultan_wallet.db")
            return DB_PATH
        except: continue
    DB_PATH = "sultan_wallet.db"
    return DB_PATH

def db():
    path = get_db_path()
    c=sqlite3.connect(path); c.row_factory=sqlite3.Row; return c
def init_db():
    try:
        c=db()
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, name TEXT, pass_hash TEXT, salt TEXT, pin_hash TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS kyc(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE, full_name TEXT, id_type TEXT, id_number TEXT, dob TEXT, birth_country TEXT, birth_governorate TEXT, birth_city TEXT, address TEXT, nationality TEXT, status TEXT DEFAULT 'pending', updated_at TEXT);
        CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, currency TEXT, balance REAL DEFAULT 0, UNIQUE(user_id,currency));
        CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, currency TEXT, amount REAL, type TEXT, ref TEXT UNIQUE, note TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS transfers(id INTEGER PRIMARY KEY AUTOINCREMENT, from_user INTEGER, to_phone TEXT, currency TEXT, amount REAL, fee REAL, status TEXT, ref TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, service_code TEXT, service_name TEXT, price REAL, currency TEXT, target TEXT, status TEXT, ref TEXT, created_at TEXT);
        """)
        c.commit(); c.close()
    except Exception as e:
        print(f"DB INIT ERROR: {e}")

def hash_pw(pw,salt=None):
    salt=salt or secrets.token_hex(16); return hashlib.sha256((salt+pw).encode()).hexdigest(), salt
def get_rates():
    try:
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/YER",timeout=3) as r:
            d=json.loads(r.read().decode()); rates=d.get("rates",{})
            return {cur: float(rates.get(cur, RATES_FALLBACK[cur])) for cur in CURRENCIES}, "مباشر"
    except: return dict(RATES_FALLBACK), "محفوظ"

def main(page: ft.Page):
    try:
        init_db()
        page.title="SULTAN WALLET"; page.rtl=True; page.theme_mode=ft.ThemeMode.DARK; page.bgcolor="#0A0A0C"; page.padding=0
        NAVY="#0B1A2A"; GOLD="#D4AF37"; CARD="#14141A"; GREEN="#10B981"; RED="#EF4444"; WHITE="#FFFFFF"; MUTED="#9CA3AF"; LIGHT="#E5E7EB"
        state={"user_id":None,"name":"","phone":"","rates":dict(RATES_FALLBACK),"rate_src":"محفوظ"}
        try:
            rates,src=get_rates(); state["rates"]=rates; state["rate_src"]=src
        except: pass
        sel_cat={"cat":"شحن جوال - اليمن"}; sel_service={"item":None}

        def snack(m):
            try:
                page.snack_bar=ft.SnackBar(ft.Text(m)); page.snack_bar.open=True; page.update()
            except: print(m)
        def bal(uid,cur):
            try:
                c=db(); r=c.execute("SELECT balance FROM accounts WHERE user_id=? AND currency=?",(uid,cur)).fetchone(); c.close(); return r["balance"] if r else 0.0
            except: return 0.0
        def ensure_accounts(uid):
            try:
                c=db()
                for cur in CURRENCIES: c.execute("INSERT OR IGNORE INTO accounts(user_id,currency,balance) VALUES(?,?,0)",(uid,cur))
                c.commit(); c.close()
            except Exception as e: print(f"ensure err {e}")
        def add_ledger(uid,cur,amount,typ,note):
            ref=f"SW-{secrets.token_hex(4).upper()}"
            c=db()
            try:
                c.execute("INSERT INTO accounts(user_id,currency,balance) VALUES(?,?,?) ON CONFLICT(user_id,currency) DO UPDATE SET balance=balance+excluded.balance",(uid,cur,amount))
                r=c.execute("SELECT balance FROM accounts WHERE user_id=? AND currency=?",(uid,cur)).fetchone()
                if r and r["balance"] < -0.0001: raise ValueError("الرصيد غير كافي")
                c.execute("INSERT INTO ledger(user_id,currency,amount,type,ref,note,created_at) VALUES(?,?,?,?,?,?,?)",(uid,cur,amount,typ,ref,note,datetime.datetime.now().isoformat()))
                c.commit(); return ref
            except Exception as e: c.rollback(); raise e
            finally: c.close()
        def kyc_status(uid):
            try:
                c=db(); r=c.execute("SELECT * FROM kyc WHERE user_id=?",(uid,)).fetchone(); c.close(); return r
            except: return None
        def total_balance_yer():
            total=0
            for cur in CURRENCIES:
                b=bal(state["user_id"],cur)
                if cur=="YER": total+=b
                else: total+= b / state["rates"].get(cur,1) if state["rates"].get(cur,0)!=0 else 0
            return total

        phone_f=ft.TextField(label="رقم الجوال", keyboard_type=ft.KeyboardType.PHONE, border_color=GOLD)
        name_f=ft.TextField(label="الاسم الكامل", border_color=GOLD)
        pass_f=ft.TextField(label="كلمة السر", password=True, can_reveal_password=True, border_color=GOLD)
        pin_f=ft.TextField(label="رمز PIN - 4 أرقام", password=True, keyboard_type=ft.KeyboardType.NUMBER, max_length=4, border_color=GOLD)
        kyc_name=ft.TextField(label="الاسم الكامل كما في الهوية *")
        kyc_id_type=ft.Dropdown(label="نوع الوثيقة *", options=[ft.dropdown.Option("جواز سفر"), ft.dropdown.Option("بطاقة شخصية")], value="بطاقة شخصية")
        kyc_id_num=ft.TextField(label="رقم الجواز / البطاقة *")
        kyc_dob=ft.TextField(label="تاريخ الميلاد * YYYY-MM-DD", hint_text="1995-05-20")
        kyc_birth_country=ft.Dropdown(label="دولة الميلاد *", options=[ft.dropdown.Option(x) for x in COUNTRIES], value="اليمن")
        kyc_birth_gov=ft.Dropdown(label="محافظة الميلاد *", options=[ft.dropdown.Option(x) for x in GOVS], value="حضرموت")
        kyc_birth_city=ft.TextField(label="مدينة / مكان الميلاد *", hint_text="المكلا")
        kyc_nationality=ft.Dropdown(label="الجنسية *", options=[ft.dropdown.Option(x) for x in COUNTRIES], value="اليمن")
        kyc_address=ft.TextField(label="العنوان الحالي *")
        to_f=ft.TextField(label="رقم حساب المستفيد / الجوال"); amt_f=ft.TextField(label="المبلغ", keyboard_type=ft.KeyboardType.NUMBER)
        cur_dd=ft.Dropdown(label="العملة", options=[ft.dropdown.Option(c) for c in CURRENCIES], value="YER")
        transfer_type=ft.Dropdown(label="نوع التحويل", options=[ft.dropdown.Option("داخلي - حساب سلطان"), ft.dropdown.Option("خارجي - بنك محلي"), ft.dropdown.Option("دولي - SWIFT")], value="داخلي - حساب سلطان")
        service_target=ft.TextField(label="رقم المستفيد *")

        def do_register(e):
            if not phone_f.value or not name_f.value or not pass_f.value or not pin_f.value: snack("عبي كل الحقول"); return
            if len(pass_f.value)<6: snack("كلمة السر 6 أحرف على الأقل"); return
            h,s=hash_pw(pass_f.value); ph,_=hash_pw(pin_f.value)
            try:
                c=db()
                cur=c.execute("INSERT INTO users(phone,name,pass_hash,salt,pin_hash,created_at) VALUES(?,?,?,?,?,?)",(phone_f.value,name_f.value,h,s,ph,datetime.datetime.now().isoformat()))
                uid=cur.lastrowid; c.commit(); c.close(); ensure_accounts(uid); state.update(user_id=uid,name=name_f.value,phone=phone_f.value); show_kyc()
            except Exception as ex:
                print(ex)
                snack("الرقم مسجل من قبل أو خطأ DB")
        def do_login(e):
            try:
                c=db(); row=c.execute("SELECT * FROM users WHERE phone=?",(phone_f.value,)).fetchone(); c.close()
                if not row: snack("الحساب غير موجود"); return
                h,_=hash_pw(pass_f.value,row["salt"])
                if h!=row["pass_hash"]: snack("كلمة السر غير صحيحة"); return
                state.update(user_id=row["id"],name=row["name"],phone=row["phone"]); ensure_accounts(row["id"])
                k=kyc_status(row["id"])
                if not k: show_kyc()
                elif k["status"]!="approved": show_kyc_status()
                else: show_home()
            except Exception as ex: snack(f"خطأ دخول: {ex}"); print(ex)
        def do_kyc(e):
            if not kyc_name.value or not kyc_id_num.value or not kyc_dob.value or not kyc_birth_city.value or not kyc_address.value: snack("عبي كل الحقول *"); return
            try:
                d=datetime.datetime.strptime(kyc_dob.value,"%Y-%m-%d"); age=(datetime.datetime.now()-d).days//365
                if age<18: snack("يجب أن يكون العمر 18+"); return
            except: snack("تاريخ الميلاد بصيغة YYYY-MM-DD"); return
            try:
                c=db(); c.execute("INSERT OR REPLACE INTO kyc(user_id,full_name,id_type,id_number,dob,birth_country,birth_governorate,birth_city,address,nationality,status,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(state["user_id"],kyc_name.value,kyc_id_type.value,kyc_id_num.value.strip().upper(),kyc_dob.value,kyc_birth_country.value,kyc_birth_gov.value,kyc_birth_city.value,kyc_address.value,kyc_nationality.value,"pending",datetime.datetime.now().isoformat())); c.commit(); c.close(); show_kyc_status()
            except Exception as ex: snack(str(ex))
        def approve_demo():
            try:
                c=db(); c.execute("UPDATE kyc SET status='approved' WHERE user_id=?",(state["user_id"],)); c.commit(); c.close(); show_home()
            except: show_home()
        def do_transfer(e):
            k=kyc_status(state["user_id"])
            if not k or k["status"]!="approved": snack("أكمل التحقق من الهوية أولاً"); show_kyc(); return
            try:
                amt=float(amt_f.value or 0)
                if amt<=0 or not to_f.value: snack("عبي المبلغ والمستفيد"); return
                cur=cur_dd.value
                if bal(state["user_id"],cur)<amt: snack("الرصيد غير كافي"); return
                fee=round(amt*0.005,2); ref=add_ledger(state["user_id"],cur,-amt,"transfer_out",f"تحويل إلى {to_f.value}")
                c=db(); r=c.execute("SELECT id FROM users WHERE phone=?",(to_f.value,)).fetchone(); c.close()
                if r and "داخلي" in transfer_type.value: ensure_accounts(r["id"]); add_ledger(r["id"],cur,amt-fee,"transfer_in",f"من {state['phone']}"); status="تم"
                else: status="قيد المعالجة"
                c=db(); c.execute("INSERT INTO transfers(from_user,to_phone,currency,amount,fee,status,ref,created_at) VALUES(?,?,?,?,?,?,?,?)",(state["user_id"],to_f.value,cur,amt,fee,status,ref,datetime.datetime.now().isoformat())); c.commit(); c.close()
                snack(f"تم التحويل - {ref}"); show_receipt(ref, amt, cur, fee, to_f.value, status)
            except Exception as ex: snack(str(ex)); print(ex)

        def bank_card(cur):
            b=bal(state["user_id"],cur) if state["user_id"] else 0
            sym={"YER":"ر.ي","SAR":"ر.س","USD":"$","AED":"د.إ"}[cur]
            acc_num=f"1001-{state['user_id'] or 0:04d}-{cur}"
            return ft.Container(width=330,height=190,border_radius=18,gradient=ft.LinearGradient(begin=ft.alignment.top_left,end=ft.alignment.bottom_right,colors=[NAVY, CARD]),padding=18,content=ft.Column([
                ft.Row([ft.Text("SULTAN BANK",size=13,weight="bold",color=GOLD), ft.Text("VISA",size=16,weight="bold",color=WHITE)]),
                ft.Text(cur,size=14,color=MUTED), ft.Text(f"{b:,.2f} {sym}",size=28,weight="bold",color=WHITE),
                ft.Text(f"رقم الحساب: {acc_num}",size=12,color=LIGHT),
                ft.Row([ft.ElevatedButton("تحويل",bgcolor=GOLD,color="black",on_click=lambda e: go_transfer(cur)), ft.ElevatedButton("شحن",bgcolor=GREEN,color="white",on_click=lambda e: topup(cur))])
            ]))
        def topup(cur):
            try: ref=add_ledger(state["user_id"],cur,1000,"topup",f"إيداع {cur}"); snack(f"تم الإيداع 1000 {cur} - {ref}"); refresh_home()
            except Exception as ex: snack(str(ex))
        def cards_row(): return ft.Row(scroll=ft.ScrollMode.AUTO, controls=[bank_card(c) for c in CURRENCIES])
        def history_text():
            if not state["user_id"]: return "سجل دخول"
            try:
                c=db(); rows=c.execute("SELECT * FROM ledger WHERE user_id=? ORDER BY id DESC LIMIT 15",(state["user_id"],)).fetchall(); c.close()
                return "\n".join([f"{r['created_at'][:16]} | {r['type']} | {r['amount']:+.2f} {r['currency']} | {r['ref']}" for r in rows]) if rows else "لا توجد عمليات"
            except: return "لا توجد عمليات"
        def orders_text():
            try:
                c=db(); rows=c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 10",(state["user_id"],)).fetchall(); c.close()
                return "\n".join([f"{r['service_name']} | {r['price']} {r['currency']} | إلى {r['target']} | {r['ref']}" for r in rows]) if rows else "لا توجد طلبات"
            except: return "لا توجد طلبات"
        history_label=ft.Text("",size=12,color=WHITE); orders_label=ft.Text("",size=12,color=WHITE); home_cards=ft.Column([])
        def refresh_home():
            try:
                home_cards.controls=[cards_row()]; history_label.value=history_text(); orders_label.value=orders_text(); page.update()
            except Exception as ex: print(f"refresh err {ex}")
        def go_transfer(cur=None):
            if cur: cur_dd.value=cur
            show_transfer()

        def header(title):
            return ft.Container(bgcolor=NAVY, padding=16, content=ft.Row([ft.Text("SULTAN WALLET", size=20, weight="bold", color=GOLD), ft.Text(title, size=14, color=WHITE)]))
        def show_auth():
            page.controls.clear()
            page.add(ft.Container(padding=20, content=ft.Column([
                ft.Container(bgcolor=NAVY, padding=20, border_radius=18, content=ft.Column([
                    ft.Text("SULTAN WALLET", size=32, weight="bold", color=GOLD, text_align="center"),
                    ft.Text("محفظتك البنكية - آمنة - دولية", size=14, color=WHITE, text_align="center"),
                    ft.Text("YER • SAR • USD • AED", size=13, color=MUTED, text_align="center"),
                ])),
                name_f, phone_f, pass_f, pin_f,
                ft.ElevatedButton("فتح حساب جديد", bgcolor=GOLD, color="black", width=400, on_click=do_register),
                ft.ElevatedButton("دخول", bgcolor=CARD, color=WHITE, width=400, on_click=do_login),
                ft.Text("بنك سلطان - حماية مصرفية: تشفير + PIN + تحقق هوية", size=11, color=MUTED, text_align="center"),
            ]))); page.update()
        def show_kyc():
            page.controls.clear(); page.add(ft.Container(padding=20, content=ft.Column([
                header("التحقق من الهوية - KYC"),
                ft.Text("لفتح حساب بنكي، يجب التحقق من هويتك.", size=13, color=MUTED),
                kyc_name, kyc_id_type, kyc_id_num, kyc_dob,
                ft.Text("مكان الميلاد", size=16, weight="bold", color=GOLD), kyc_birth_country, kyc_birth_gov, kyc_birth_city,
                kyc_nationality, kyc_address,
                ft.ElevatedButton("إرسال للمراجعة البنكية", bgcolor=GOLD, color="black", width=400, on_click=do_kyc),
                ft.TextButton("تخطي لاحقاً", on_click=lambda e: show_home()),
            ], scroll=ft.ScrollMode.AUTO))); page.update()
        def show_kyc_status():
            k=kyc_status(state["user_id"]); txt="قيد المراجعة البنكية" if k and k["status"]=="pending" else "تم التحقق - حسابك مفعل ✅"
            page.controls.clear(); page.add(ft.Container(padding=20, content=ft.Column([
                header("حالة الحساب"),
                ft.Text(txt, size=16, color=GOLD),
                ft.Text(f"{k['full_name'] if k else ''}\n{k['id_type'] if k else ''} - {k['id_number'] if k else ''}\nالميلاد: {k['dob'] if k else ''}", size=13, color=WHITE),
                ft.ElevatedButton("تفعيل الحساب - دخول", bgcolor=GREEN, color="white", width=400, on_click=lambda e: approve_demo()),
                ft.ElevatedButton("تعديل البيانات", bgcolor=CARD, color=WHITE, width=400, on_click=lambda e: show_kyc()),
                ft.TextButton("خروج", on_click=lambda e: show_auth()),
            ]))); page.update()
        def show_home():
            total=total_balance_yer()
            page.controls.clear(); page.add(ft.Container(padding=16, content=ft.Column([
                header(f"أهلاً {state['name']}"),
                ft.Container(bgcolor=NAVY, padding=16, border_radius=16, content=ft.Column([
                    ft.Text("إجمالي الأرصدة (بالريال اليمني تقريباً)", size=12, color=MUTED),
                    ft.Text(f"{total:,.2f} ر.ي", size=26, weight="bold", color=WHITE),
                    ft.Text(f"أسعار الصرف: {state['rate_src']}", size=11, color=MUTED),
                ])),
                ft.Text("حساباتي - اسحب يمين / يسار", size=14, weight="bold", color=GOLD),
                home_cards,
                ft.Text("خدمات بنكية", size=16, weight="bold", color=GOLD),
                ft.Row([ft.ElevatedButton("💸 تحويل", bgcolor=GOLD, color="black", width=110, on_click=lambda e: show_transfer()),
                        ft.ElevatedButton("📱 شحن", bgcolor=CARD, color=WHITE, width=110, on_click=lambda e: show_services_cat("شحن جوال - اليمن")),
                        ft.ElevatedButton("🎮 ألعاب", bgcolor=CARD, color=WHITE, width=110, on_click=lambda e: show_services_cat("ألعاب وشحن عملات"))]),
                ft.Row([ft.ElevatedButton("💳 بطاقات", bgcolor=CARD, color=WHITE, width=110, on_click=lambda e: show_services_cat("بطاقات واشتراكات")),
                        ft.ElevatedButton("🌍 دولي", bgcolor=CARD, color=WHITE, width=110, on_click=lambda e: show_services_cat("شحن جوال - دول أخرى")),
                        ft.ElevatedButton("🪪 حسابي", bgcolor=CARD, color=WHITE, width=110, on_click=lambda e: show_kyc_status())]),
                ft.Text("كشف الحساب", size=16, weight="bold", color=GOLD), history_label,
                ft.Text("طلبات الخدمات", size=16, weight="bold", color=GOLD), orders_label,
                ft.Text("خدمة العملاء: support@sultanwallet.com - 24/7", size=11, color=MUTED),
            ]))); refresh_home()
        def show_transfer():
            page.controls.clear(); page.add(ft.Container(padding=20, content=ft.Column([
                header("تحويل بنكي"),
                transfer_type, to_f, amt_f, cur_dd,
                ft.ElevatedButton("تأكيد التحويل", bgcolor=GOLD, color="black", width=400, on_click=do_transfer),
                ft.ElevatedButton("رجوع", bgcolor=CARD, color=WHITE, width=400, on_click=lambda e: show_home()),
                ft.Text("رسوم التحويل 0.5% - التحويل الداخلي فوري", size=11, color=MUTED),
            ]))); page.update()
        def show_receipt(ref, amt, cur, fee, to_phone, status):
            page.controls.clear(); page.add(ft.Container(padding=20, content=ft.Column([
                header("إيصال التحويل"),
                ft.Container(bgcolor=CARD, padding=16, border_radius=16, content=ft.Column([
                    ft.Text("تم التحويل بنجاح ✅", size=20, weight="bold", color=GREEN),
                    ft.Text(f"المبلغ: {amt} {cur}", size=16, color=WHITE),
                    ft.Text(f"إلى: {to_phone}", size=14, color=WHITE),
                    ft.Text(f"الرسوم: {fee} {cur}", size=14, color=WHITE),
                    ft.Text(f"الرقم المرجعي: {ref}", size=14, weight="bold", color=GOLD),
                    ft.Text(f"الحالة: {status}", size=14, color=WHITE),
                    ft.Text(f"التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", size=12, color=MUTED),
                ])),
                ft.ElevatedButton("رجوع للرئيسية", bgcolor=GOLD, color="black", width=400, on_click=lambda e: show_home()),
            ]))); page.update()
        def show_services_cat(cat):
            sel_cat["cat"]=cat; show_services()
        def show_services():
            def on_cat(cat): sel_cat["cat"]=cat; show_services()
            def on_pick(item): sel_service["item"]=item; show_services()
            cats=list(SERVICES.keys())
            cat_row=ft.Row(scroll=ft.ScrollMode.AUTO, controls=[ft.ElevatedButton(c, bgcolor=GOLD if c==sel_cat["cat"] else CARD, color="black" if c==sel_cat["cat"] else WHITE, on_click=lambda e, c=c: on_cat(c)) for c in cats])
            items=SERVICES[sel_cat["cat"]]
            cards=[]
            for it in items:
                sel = sel_service["item"] and sel_service["item"]["code"]==it["code"]
                cards.append(ft.Container(width=340, border_radius=14, bgcolor=GREEN if sel else CARD, padding=12, on_click=lambda e, it=it: on_pick(it), content=ft.Column([
                    ft.Text(it["name"], size=15, weight="bold", color="black" if sel else WHITE),
                    ft.Text(f"السعر: {it['price']} {it['cur']} • كود: {it['code']}", size=12, color="black" if sel else GOLD),
                ])))
            sel_txt=f"المختار: {sel_service['item']['name']} - {sel_service['item']['price']} {sel_service['item']['cur']}" if sel_service["item"] else "اختر خدمة"
            page.controls.clear(); page.add(ft.Container(padding=16, content=ft.Column([
                header("الخدمات البنكية"),
                cat_row,
                ft.Column(cards, scroll=ft.ScrollMode.AUTO, height=320),
                ft.Text(sel_txt, size=14, weight="bold", color=GOLD),
                service_target,
                ft.ElevatedButton("تأكيد الدفع من الحساب", bgcolor=GOLD, color="black", width=400, on_click=buy_service),
                ft.ElevatedButton("رجوع", bgcolor=CARD, color=WHITE, width=400, on_click=lambda e: show_home()),
            ], scroll=ft.ScrollMode.AUTO))); page.update()
        def buy_service(e):
            item=sel_service["item"]
            if not item: snack("اختر خدمة"); return
            if not service_target.value: snack("اكتب رقم المستفيد"); return
            k=kyc_status(state["user_id"])
            if not k or k["status"]!="approved": snack("أكمل التحقق أولاً"); show_kyc(); return
            cur=item["cur"]; price=item["price"]
            if bal(state["user_id"],cur) < price: snack(f"الرصيد غير كافي - تحتاج {price} {cur}"); return
            try:
                ref=add_ledger(state["user_id"],cur,-price,"service_buy",f"{item['name']} -> {service_target.value}")
                c=db(); c.execute("INSERT INTO orders(user_id,service_code,service_name,price,currency,target,status,ref,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(state["user_id"],item["code"],item["name"],price,cur,service_target.value,"تم",ref,datetime.datetime.now().isoformat())); c.commit(); c.close()
                snack(f"تم الدفع ✅ {item['name']} - {ref}"); show_home()
            except Exception as ex: snack(str(ex)); print(ex)

        show_auth()
    except Exception as e:
        print(f"FATAL: {e}")
        import traceback; traceback.print_exc()
        try:
            page.controls.clear()
            page.add(ft.Text(f"خطأ بدء: {e}", color="red"))
            page.update()
        except: pass

ft.app(target=main)
