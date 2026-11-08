# SULTAN WALLET V3.4 - INTERNATIONAL - All Countries: Each feature has its own page - Full Commercial - KYC + Wallet + ALL Services
# خدمات متكاملة: شحن جوال، انترنت، بطاقات ألعاب، عملات تطبيقات، منصات، ترفيه
import flet as ft
import sqlite3, hashlib, secrets, json, urllib.request, datetime, re

DB="sultan_wallet.db"
CURRENCIES=["YER","SAR","USD","AED"]
RATES_FALLBACK={"YER":1.0,"SAR":0.00066,"USD":0.0025,"AED":0.0092}
GOVS=["صنعاء","عدن","تعز","حضرموت","الحديدة","إب","ذمار","مأرب","الجوف","شبوة","أبين","لحج","الضالع","البيضاء","حجة","صعدة","المحويت","عمران","ريمة","المهرة","سقطرى"]
COUNTRIES=["اليمن","السعودية","الإمارات","قطر","الكويت","عمان","البحرين","الأردن","مصر","السودان","أخرى"]

# ===== كتالوج الخدمات الكامل =====
SERVICES = {
 "شحن جوال - اليمن": [
   {"name":"يمن موبايل - 500","price":500,"cur":"YER","code":"YM-500","desc":"شحن يمن موبايل"},
   {"name":"يمن موبايل - 1000","price":1000,"cur":"YER","code":"YM-1000","desc":"شحن يمن موبايل"},
   {"name":"سبأفون - 1000","price":1000,"cur":"YER","code":"SABA-1000","desc":"شحن سبأفون"},
   {"name":"MTN يمن - 1000","price":1000,"cur":"YER","code":"MTN-1000","desc":"شحن MTN يمن"},
   {"name":"YOU - 1000","price":1000,"cur":"YER","code":"YOU-1000","desc":"شحن YOU"},
 ],
 "شحن جوال - السعودية": [
   {"name":"STC سوا - 10 ر.س","price":10,"cur":"SAR","code":"STC-10","desc":"شحن سوا STC السعودية"},
   {"name":"STC سوا - 20 ر.س","price":20,"cur":"SAR","code":"STC-20","desc":"شحن سوا"},
   {"name":"STC سوا - 50 ر.س","price":50,"cur":"SAR","code":"STC-50","desc":"شحن سوا"},
   {"name":"موبايلي - 10 ر.س","price":10,"cur":"SAR","code":"MOB-10","desc":"شحن موبايلي"},
   {"name":"موبايلي - 30 ر.س","price":30,"cur":"SAR","code":"MOB-30","desc":"شحن موبايلي"},
   {"name":"زين السعودية - 15 ر.س","price":15,"cur":"SAR","code":"ZAIN-SA-15","desc":"شحن زين السعودية"},
   {"name":"زين السعودية - 50 ر.س","price":50,"cur":"SAR","code":"ZAIN-SA-50","desc":"شحن زين السعودية"},
   {"name":"Virgin Mobile SA - 20 ر.س","price":20,"cur":"SAR","code":"VIR-SA-20","desc":"شحن فيرجن"},
   {"name":"Lebara SA - 15 ر.س","price":15,"cur":"SAR","code":"LEB-SA-15","desc":"شحن ليبارا السعودية"},
 ],
 "شحن جوال - الإمارات": [
   {"name":"Etisalat UAE - 30 د.إ","price":30,"cur":"AED","code":"ETI-30","desc":"شحن اتصالات الإمارات"},
   {"name":"Etisalat UAE - 50 د.إ","price":50,"cur":"AED","code":"ETI-50","desc":"شحن اتصالات"},
   {"name":"du UAE - 30 د.إ","price":30,"cur":"AED","code":"DU-30","desc":"شحن دو الإمارات"},
   {"name":"du UAE - 50 د.إ","price":50,"cur":"AED","code":"DU-50","desc":"شحن دو"},
   {"name":"Virgin UAE - 30 د.إ","price":30,"cur":"AED","code":"VIR-AE-30","desc":"شحن فيرجن الإمارات"},
 ],
 "شحن جوال - مصر": [
   {"name":"Vodafone مصر - 50 ج.م","price":50,"cur":"USD","code":"VOD-EG-50","desc":"شحن فودافون مصر - يعادل بالدولار"},
   {"name":"Orange مصر - 50 ج.م","price":50,"cur":"USD","code":"ORG-EG-50","desc":"شحن أورانج مصر"},
   {"name":"Etisalat مصر - 50 ج.م","price":50,"cur":"USD","code":"ETI-EG-50","desc":"شحن اتصالات مصر"},
   {"name":"WE مصر - 50 ج.م","price":50,"cur":"USD","code":"WE-EG-50","desc":"شحن وي مصر"},
 ],
 "شحن جوال - الأردن": [
   {"name":"Zain الأردن - 5 د.أ","price":5,"cur":"USD","code":"ZAIN-JO-5","desc":"شحن زين الأردن"},
   {"name":"Orange الأردن - 5 د.أ","price":5,"cur":"USD","code":"ORG-JO-5","desc":"شحن أورانج الأردن"},
   {"name":"Umniah - 5 د.أ","price":5,"cur":"USD","code":"UMN-JO-5","desc":"شحن أمنية"},
 ],
 "شحن جوال - دول أخرى": [
   {"name":"Kuwait - Zain KW 5 د.ك","price":5,"cur":"USD","code":"ZAIN-KW-5","desc":"شحن زين الكويت"},
   {"name":"Kuwait - Ooredoo KW","price":5,"cur":"USD","code":"OOR-KW-5","desc":"شحن أوريدو الكويت"},
   {"name":"Qatar - Ooredoo QA","price":5,"cur":"USD","code":"OOR-QA-5","desc":"شحن أوريدو قطر"},
   {"name":"Bahrain - Batelco","price":5,"cur":"USD","code":"BAT-BH-5","desc":"شحن بتلكو البحرين"},
   {"name":"Oman - Omantel","price":5,"cur":"USD","code":"OMAN-5","desc":"شحن عمانتل"},
   {"name":"Iraq - Zain IQ","price":5,"cur":"USD","code":"ZAIN-IQ-5","desc":"شحن زين العراق"},
   {"name":"Sudan - MTN SD","price":5,"cur":"USD","code":"MTN-SD-5","desc":"شحن MTN السودان"},
   {"name":"Turkey - Turkcell","price":5,"cur":"USD","code":"TURK-5","desc":"شحن تركسل تركيا"},
 ],
 "كروت انترنت": [
   {"name":"كرت يمن نت 5GB","price":3000,"cur":"YER","code":"YNET-5","desc":"كرت انترنت يمن نت"},
   {"name":"كرت يمن نت 10GB","price":5500,"cur":"YER","code":"YNET-10","desc":"كرت انترنت يمن نت"},
   {"name":"STC انترنت - السعودية","price":50,"cur":"SAR","code":"STC-NET-50","desc":"باقة انترنت STC"},
   {"name":"Etisalat انترنت - الإمارات","price":50,"cur":"AED","code":"ETI-NET-50","desc":"باقة انترنت اتصالات"},
 ],
 "ألعاب وشحن عملات": [
   {"name":"PUBG - 60 شدة UC","price":0.99,"cur":"USD","code":"PUBG-60","desc":"60 شدة PUBG Mobile"},
   {"name":"PUBG - 325 شدة UC","price":4.99,"cur":"USD","code":"PUBG-325","desc":"325 شدة"},
   {"name":"PUBG - 660 شدة UC","price":9.99,"cur":"USD","code":"PUBG-660","desc":"660 شدة"},
   {"name":"Free Fire - 100 جوهرة","price":0.99,"cur":"USD","code":"FF-100","desc":"100 جوهرة"},
   {"name":"Free Fire - 1060 جوهرة","price":9.99,"cur":"USD","code":"FF-1060","desc":"1060 جوهرة"},
   {"name":"Fortnite - 1000 V-Bucks","price":8.99,"cur":"USD","code":"FN-1000","desc":"1000 V-Bucks"},
   {"name":"Roblox - 400 Robux","price":4.99,"cur":"USD","code":"RB-400","desc":"400 Robux"},
   {"name":"TikTok - 70 كوين","price":0.99,"cur":"USD","code":"TT-70","desc":"70 كوين تيك توك"},
   {"name":"TikTok - 700 كوين","price":9.99,"cur":"USD","code":"TT-700","desc":"700 كوين"},
   {"name":"PlayStation - 10$","price":10,"cur":"USD","code":"PS-10","desc":"بطاقة بلايستيشن"},
   {"name":"Xbox - 10$","price":10,"cur":"USD","code":"XB-10","desc":"بطاقة اكس بوكس"},
 ],
 "بطاقات واشتراكات": [
   {"name":"Google Play - 5$","price":5,"cur":"USD","code":"GP-5","desc":"بطاقة جوجل بلاي - دولي"},
   {"name":"Google Play - 10$","price":10,"cur":"USD","code":"GP-10","desc":"بطاقة جوجل بلاي"},
   {"name":"Google Play - 25$","price":25,"cur":"USD","code":"GP-25","desc":"بطاقة جوجل بلاي"},
   {"name":"iTunes / Apple - 10$","price":10,"cur":"USD","code":"AP-10","desc":"بطاقة ابل - دولي"},
   {"name":"iTunes / Apple - 25$","price":25,"cur":"USD","code":"AP-25","desc":"بطاقة ابل"},
   {"name":"Netflix - شهر - دولي","price":9.99,"cur":"USD","code":"NF-1M","desc":"اشتراك نتفليكس"},
   {"name":"Shahid VIP - شهر","price":8.99,"cur":"USD","code":"SH-1M","desc":"اشتراك شاهد"},
   {"name":"Disney+ - شهر","price":7.99,"cur":"USD","code":"DS-1M","desc":"اشتراك ديزني"},
   {"name":"YouTube Premium - شهر","price":11.99,"cur":"USD","code":"YT-1M","desc":"يوتيوب بريميوم"},
   {"name":"Spotify - شهر","price":9.99,"cur":"USD","code":"SP-1M","desc":"سبوتيفاي"},
   {"name":"Amazon Prime - شهر","price":8.99,"cur":"USD","code":"AM-1M","desc":"امازون برايم"},
   {"name":"ChatGPT Plus - شهر","price":20,"cur":"USD","code":"GPT-1M","desc":"شات جي بي تي بلس"},
   {"name":"iTunes السعودية - 50 ر.س","price":50,"cur":"SAR","code":"AP-SA-50","desc":"بطاقة ابل السعودية"},
   {"name":"Google Play السعودية - 50 ر.س","price":50,"cur":"SAR","code":"GP-SA-50","desc":"بطاقة جوجل السعودية"},
   {"name":"iTunes الإمارات - 50 د.إ","price":50,"cur":"AED","code":"AP-AE-50","desc":"بطاقة ابل الإمارات"},
 ],
 "خدمات أخرى - دولي": [
   {"name":"شحن محفظة بايير","price":10,"cur":"USD","code":"PAYEER-10","desc":"شحن بايير"},
   {"name":"شحن Perfect Money","price":10,"cur":"USD","code":"PM-10","desc":"شحن بيرفكت موني"},
   {"name":"كهرباء - اليمن","price":5000,"cur":"YER","code":"ELEC-1","desc":"دفع فاتورة كهرباء اليمن"},
   {"name":"كهرباء - السعودية","price":50,"cur":"SAR","code":"ELEC-SA","desc":"دفع فاتورة كهرباء السعودية"},
   {"name":"مياه - اليمن","price":3000,"cur":"YER","code":"WATER-1","desc":"دفع فاتورة مياه"},
   {"name":"انترنت منزلي - اليمن","price":8000,"cur":"YER","code":"HOME-NET","desc":"تجديد انترنت منزلي"},
 ],
}
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
    c=db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, name TEXT, pass_hash TEXT, salt TEXT, pin_hash TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS kyc(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE, full_name TEXT, id_type TEXT, id_number TEXT, dob TEXT, birth_country TEXT, birth_governorate TEXT, birth_city TEXT, address TEXT, nationality TEXT, id_front TEXT, id_back TEXT, selfie TEXT, status TEXT DEFAULT 'pending', updated_at TEXT);
    CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, currency TEXT, balance REAL DEFAULT 0, UNIQUE(user_id,currency));
    CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, currency TEXT, amount REAL, type TEXT, ref TEXT UNIQUE, note TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS transfers(id INTEGER PRIMARY KEY AUTOINCREMENT, from_user INTEGER, to_phone TEXT, currency TEXT, amount REAL, fee REAL, status TEXT, ref TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, service_code TEXT, service_name TEXT, price REAL, currency TEXT, target TEXT, status TEXT, ref TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS security_log(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, device TEXT, created_at TEXT);
    """)
    c.commit(); c.close()
def hash_pw(pw,salt=None):
    salt=salt or secrets.token_hex(16); return hashlib.sha256((salt+pw).encode()).hexdigest(), salt
def get_rates():
    try:
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/YER",timeout=5) as r:
            d=json.loads(r.read().decode()); rates=d.get("rates",{})
            return {cur: float(rates.get(cur, {"YER":1.0,"SAR":0.00066,"USD":0.0025,"AED":0.0092}[cur])) for cur in CURRENCIES}, "مباشر"
    except: return {"YER":1.0,"SAR":0.00066,"USD":0.0025,"AED":0.0092}, "محفوظ"

def main(page: ft.Page):
    init_db()
    page.title="SULTAN WALLET"; page.rtl=True; page.theme_mode=ft.ThemeMode.DARK; page.bgcolor="#050507"; page.padding=0; page.scroll=ft.ScrollMode.AUTO
    GOLD="#D4AF37"; CARD="#121214"; GREEN="#10B981"; RED="#EF4444"; WHITE="#FFFFFF"; MUTED="#9CA3AF"; ORANGE="#F59E0B"; BLUE="#3B82F6"
    state={"user_id":None,"name":"","phone":"","rates":{"YER":1.0,"SAR":0.00066,"USD":0.0025,"AED":0.0092},"rate_src":""}
    rates,src=get_rates(); state["rates"]=rates; state["rate_src"]=src
    selected_cat={"cat":"شحن جوال"}; selected_service={"item":None}

    def snack(m): page.snack_bar=ft.SnackBar(ft.Text(m)); page.snack_bar.open=True; page.update()
    def log_action(uid,act):
        c=db(); c.execute("INSERT INTO security_log(user_id,action,device,created_at) VALUES(?,?,?,?)",(uid,act,"Android",datetime.datetime.now().isoformat())); c.commit(); c.close()
    def bal(uid,cur):
        c=db(); r=c.execute("SELECT balance FROM accounts WHERE user_id=? AND currency=?",(uid,cur)).fetchone(); c.close(); return r["balance"] if r else 0.0
    def ensure_accounts(uid):
        c=db()
        for cur in CURRENCIES: c.execute("INSERT OR IGNORE INTO accounts(user_id,currency,balance) VALUES(?,?,0)",(uid,cur))
        c.commit(); c.close()
    def add_ledger(uid,cur,amount,typ,note):
        ref=f"SL-{secrets.token_hex(6).upper()}"
        c=db()
        try:
            c.execute("INSERT INTO accounts(user_id,currency,balance) VALUES(?,?,?) ON CONFLICT(user_id,currency) DO UPDATE SET balance=balance+excluded.balance",(uid,cur,amount))
            r=c.execute("SELECT balance FROM accounts WHERE user_id=? AND currency=?",(uid,cur)).fetchone()
            if r["balance"] < -0.0001: raise ValueError("الرصيد غير كافي")
            c.execute("INSERT INTO ledger(user_id,currency,amount,type,ref,note,created_at) VALUES(?,?,?,?,?,?,?)",(uid,cur,amount,typ,ref,note,datetime.datetime.now().isoformat()))
            c.commit(); return ref
        except Exception as e: c.rollback(); raise e
        finally: c.close()
    def kyc_status(uid):
        c=db(); r=c.execute("SELECT * FROM kyc WHERE user_id=?",(uid,)).fetchone(); c.close(); return r

    phone_f=ft.TextField(label="رقم الجوال *", keyboard_type=ft.KeyboardType.PHONE)
    name_f=ft.TextField(label="الاسم الكامل *")
    pass_f=ft.TextField(label="كلمة السر *", password=True, can_reveal_password=True)
    pin_f=ft.TextField(label="PIN من 4 أرقام *", password=True, keyboard_type=ft.KeyboardType.NUMBER, max_length=4)
    kyc_name=ft.TextField(label="الاسم كما في الهوية *")
    kyc_id_type=ft.Dropdown(label="نوع الوثيقة *", options=[ft.dropdown.Option("جواز سفر"), ft.dropdown.Option("بطاقة شخصية")], value="بطاقة شخصية")
    kyc_id_num=ft.TextField(label="رقم الجواز / البطاقة *")
    kyc_dob=ft.TextField(label="تاريخ الميلاد * YYYY-MM-DD", hint_text="1995-05-20")
    kyc_birth_country=ft.Dropdown(label="دولة الميلاد *", options=[ft.dropdown.Option(x) for x in COUNTRIES], value="اليمن")
    kyc_birth_gov=ft.Dropdown(label="محافظة الميلاد *", options=[ft.dropdown.Option(x) for x in GOVS], value="حضرموت")
    kyc_birth_city=ft.TextField(label="مدينة / مكان الميلاد *", hint_text="المكلا")
    kyc_nationality=ft.Dropdown(label="الجنسية *", options=[ft.dropdown.Option(x) for x in COUNTRIES], value="اليمن")
    kyc_address=ft.TextField(label="العنوان الحالي *")
    kyc_front=ft.TextField(label="صورة الوثيقة - أمامي"); kyc_back=ft.TextField(label="صورة الوثيقة - خلفي"); kyc_selfie=ft.TextField(label="سيلفي مع الوثيقة")
    to_f=ft.TextField(label="رقم المستلم"); amt_f=ft.TextField(label="المبلغ", keyboard_type=ft.KeyboardType.NUMBER)
    cur_dd=ft.Dropdown(label="العملة", options=[ft.dropdown.Option(c) for c in CURRENCIES], value="YER")
    transfer_type=ft.Dropdown(label="نوع التحويل", options=[ft.dropdown.Option("داخلي"), ft.dropdown.Option("خارجي - بنك محلي"), ft.dropdown.Option("دولي")], value="داخلي")
    service_target=ft.TextField(label="رقم الجوال / الحساب المراد شحنه *", hint_text="رقم المستفيد من الخدمة")
    service_note=ft.TextField(label="ملاحظة (اختياري)")

    def do_register(e):
        if not phone_f.value or not name_f.value or not pass_f.value or not pin_f.value: snack("عبي كل الحقول"); return
        if len(pass_f.value)<8: snack("كلمة السر 8 أحرف على الأقل"); return
        h,s=hash_pw(pass_f.value); ph,_=hash_pw(pin_f.value)
        c=db()
        try:
            cur=c.execute("INSERT INTO users(phone,name,pass_hash,salt,pin_hash,created_at) VALUES(?,?,?,?,?,?)",(phone_f.value,name_f.value,h,s,ph,datetime.datetime.now().isoformat()))
            uid=cur.lastrowid; c.commit(); c.close(); ensure_accounts(uid); state.update(user_id=uid,name=name_f.value,phone=phone_f.value); log_action(uid,"إنشاء حساب"); show_kyc()
        except sqlite3.IntegrityError: snack("الرقم مسجل من قبل"); c.close()
    def do_login(e):
        c=db(); row=c.execute("SELECT * FROM users WHERE phone=?",(phone_f.value,)).fetchone(); c.close()
        if not row: snack("الحساب غير موجود"); return
        h,_=hash_pw(pass_f.value,row["salt"])
        if h!=row["pass_hash"]: snack("كلمة السر غلط"); return
        state.update(user_id=row["id"],name=row["name"],phone=row["phone"]); ensure_accounts(row["id"]); log_action(row["id"],"دخول")
        k=kyc_status(row["id"])
        if not k: show_kyc()
        elif k["status"]!="approved": show_kyc_status()
        else: show_home()
    def do_kyc(e):
        if not kyc_name.value or not kyc_id_num.value or not kyc_dob.value or not kyc_birth_city.value or not kyc_address.value: snack("عبي كل الحقول *"); return
        try:
            d=datetime.datetime.strptime(kyc_dob.value,"%Y-%m-%d"); age=(datetime.datetime.now()-d).days//365
            if age<18: snack("لازم عمرك 18+"); return
        except: snack("تاريخ الميلاد بصيغة YYYY-MM-DD"); return
        c=db(); c.execute("INSERT OR REPLACE INTO kyc(user_id,full_name,id_type,id_number,dob,birth_country,birth_governorate,birth_city,address,nationality,id_front,id_back,selfie,status,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(state["user_id"],kyc_name.value,kyc_id_type.value,kyc_id_num.value.strip().upper(),kyc_dob.value,kyc_birth_country.value,kyc_birth_gov.value,kyc_birth_city.value,kyc_address.value,kyc_nationality.value,kyc_front.value,kyc_back.value,kyc_selfie.value,"pending",datetime.datetime.now().isoformat())); c.commit(); c.close(); show_kyc_status()
    def approve_demo():
        c=db(); c.execute("UPDATE kyc SET status='approved' WHERE user_id=?",(state["user_id"],)); c.commit(); c.close(); show_home()
    def do_transfer(e):
        k=kyc_status(state["user_id"])
        if not k or k["status"]!="approved": snack("أكمل KYC أولاً"); show_kyc(); return
        try:
            amt=float(amt_f.value or 0)
            if amt<=0 or not to_f.value: snack("عبي المبلغ والمستلم"); return
            cur=cur_dd.value
            if bal(state["user_id"],cur)<amt: snack("الرصيد غير كافي"); return
            fee=round(amt*0.005,2); ref=add_ledger(state["user_id"],cur,-amt,"transfer_out",f"تحويل إلى {to_f.value}")
            c=db(); r=c.execute("SELECT id FROM users WHERE phone=?",(to_f.value,)).fetchone(); c.close()
            if r and transfer_type.value=="داخلي": ensure_accounts(r["id"]); add_ledger(r["id"],cur,amt-fee,"transfer_in",f"من {state['phone']}"); status="تم - فوري"
            else: status="قيد المعالجة"
            c=db(); c.execute("INSERT INTO transfers(from_user,to_phone,currency,amount,fee,status,ref,created_at) VALUES(?,?,?,?,?,?,?,?)",(state["user_id"],to_f.value,cur,amt,fee,status,ref,datetime.datetime.now().isoformat())); c.commit(); c.close()
            snack(f"تم التحويل {amt} {cur} - {ref}"); show_home()
        except Exception as ex: snack(str(ex))

    # ===== الخدمات =====
    def buy_service(e):
        item=selected_service["item"]
        if not item: snack("اختر خدمة أولاً"); return
        if not service_target.value: snack("اكتب رقم المستفيد"); return
        k=kyc_status(state["user_id"])
        if not k or k["status"]!="approved": snack("أكمل KYC قبل الشراء"); show_kyc(); return
        cur=item["cur"]; price=item["price"]
        if bal(state["user_id"],cur) < price: snack(f"الرصيد غير كافي - تحتاج {price} {cur} - رصيدك {bal(state['user_id'],cur):.2f}"); return
        try:
            ref=add_ledger(state["user_id"],cur,-price,"service_buy",f"{item['name']} -> {service_target.value}")
            c=db(); c.execute("INSERT INTO orders(user_id,service_code,service_name,price,currency,target,status,ref,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(state["user_id"],item["code"],item["name"],price,cur,service_target.value,"تم - سلم الكود للمستفيد",ref,datetime.datetime.now().isoformat())); c.commit(); c.close()
            log_action(state["user_id"],f"شراء خدمة {item['name']}")
            snack(f"تم الشراء ✅ {item['name']} - {price} {cur} - {ref}"); refresh_home(); show_services()
        except Exception as ex: snack(str(ex))

    def card(cur):
        b=bal(state["user_id"],cur) if state["user_id"] else 0
        sym={"YER":"ر.ي","SAR":"ر.س","USD":"$","AED":"د.إ"}[cur]
        return ft.Container(width=320,height=180,border_radius=20,bgcolor=CARD,padding=20,content=ft.Column([
            ft.Row([ft.Text(cur,size=20,weight="bold",color=GOLD), ft.Text("SULTAN WALLET",size=11,color=MUTED)]),
            ft.Text(f"{b:,.2f} {sym}",size=28,weight="bold",color=WHITE),
            ft.Text(f"1 YER = {state['rates'].get(cur,0):.4f} {cur} • {state['rate_src']}",size=11,color=MUTED),
            ft.Row([ft.ElevatedButton("إرسال",bgcolor=GOLD,color="black",on_click=lambda e: go_transfer(cur)), ft.ElevatedButton("شحن +1000",bgcolor=GREEN,color="white",on_click=lambda e: topup(cur))])
        ]))
    def topup(cur):
        try: ref=add_ledger(state["user_id"],cur,1000,"topup",f"شحن {cur}"); snack(f"تم الشحن 1000 {cur} - {ref}"); refresh_home()
        except Exception as ex: snack(str(ex))
    def cards_row(): return ft.Row(scroll=ft.ScrollMode.AUTO, controls=[card(c) for c in CURRENCIES])
    def history_text():
        if not state["user_id"]: return "سجل دخول"
        c=db(); rows=c.execute("SELECT * FROM ledger WHERE user_id=? ORDER BY id DESC LIMIT 15",(state["user_id"],)).fetchall(); c.close()
        return "\n".join([f"{r['created_at'][:16]} | {r['type']} | {r['amount']:+.2f} {r['currency']} | {r['ref']}" for r in rows]) if rows else "لا توجد عمليات"
    def orders_text():
        c=db(); rows=c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 10",(state["user_id"],)).fetchall(); c.close()
        return "\n".join([f"{r['service_name']} | {r['price']} {r['currency']} | إلى {r['target']} | {r['status']} | {r['ref']}" for r in rows]) if rows else "لا توجد طلبات بعد"
    history_label=ft.Text("",size=12,color=WHITE); orders_label=ft.Text("",size=12,color=WHITE); home_cards=ft.Column([])
    gold_label=ft.Text("ذهب 24: 98.5 $  •  21: 86.2 $  •  18: 73.9 $  •  فضة: 1.2 $ / غرام",size=13,color=GOLD)
    def refresh_home(): home_cards.controls=[cards_row()]; history_label.value=history_text(); orders_label.value=orders_text(); page.update()
    def go_transfer(cur=None):
        if cur: cur_dd.value=cur
        show_transfer()


    def show_services_cat(cat):
        selected_cat["cat"]=cat
        # reset selection
        show_services()
    def show_gold_page():
        page.controls.clear()
        page.add(ft.Container(padding=20,content=ft.Column([
            ft.Text("أسعار الذهب والعملات",size=24,weight="bold",color=GOLD),
            ft.Text("ذهب 24: 98.5 $ / غرام",size=18,color=WHITE),
            ft.Text("ذهب 22: 90.3 $ / غرام",size=18,color=WHITE),
            ft.Text("ذهب 21: 86.2 $ / غرام",size=18,color=WHITE),
            ft.Text("ذهب 18: 73.9 $ / غرام",size=18,color=WHITE),
            ft.Text("فضة: 1.2 $ / غرام",size=18,color=WHITE),
            ft.Text(f"صرف: 1 YER = {state['rates'].get('SAR',0):.4f} SAR | {state['rates'].get('USD',0):.4f} USD | {state['rates'].get('AED',0):.4f} AED",size=14,color=MUTED),
            ft.Text("حاسبة الذهب: اكتب الوزن بالغرام",size=14,color=GOLD),
            ft.ElevatedButton("رجوع للرئيسية",bgcolor=CARD,color=WHITE,width=400,on_click=lambda e: show_home()),
            ft.ElevatedButton("شحن رصيد",bgcolor=GOLD,color="black",width=400,on_click=lambda e: show_services_cat("شحن جوال")),
        ]))); page.update()
    def show_auth():
        page.controls.clear(); page.add(ft.Container(padding=20,content=ft.Column([
            ft.Text("SULTAN WALLET",size=32,weight="bold",color=GOLD,text_align="center"),
            ft.Text("محفظة دولية - اليمن • السعودية • الإمارات • مصر • الأردن • الخليج • دولي",size=14,color=MUTED,text_align="center"),
            ft.Text("4 عملات • KYC كامل • حماية + PIN + سجل أمان",size=12,color=GREEN,text_align="center"),
            name_f, phone_f, pass_f, pin_f,
            ft.ElevatedButton("إنشاء حساب جديد",bgcolor=GOLD,color="black",width=400,on_click=do_register),
            ft.ElevatedButton("دخول",bgcolor=CARD,color=WHITE,width=400,on_click=do_login),
        ]))); page.update()
    def show_kyc():
        page.controls.clear(); page.add(ft.Container(padding=20,content=ft.Column([
            ft.Text("التحقق من الهوية - KYC",size=24,weight="bold",color=GOLD),
            ft.Text("جواز سفر أو بطاقة شخصية + تاريخ ومكان الميلاد",size=13,color=MUTED),
            kyc_name, kyc_id_type, kyc_id_num, kyc_dob,
            ft.Text("مكان الميلاد",size=16,weight="bold",color=GOLD), kyc_birth_country, kyc_birth_gov, kyc_birth_city,
            kyc_nationality, kyc_address, kyc_front, kyc_back, kyc_selfie,
            ft.ElevatedButton("إرسال للمراجعة",bgcolor=GOLD,color="black",width=400,on_click=do_kyc),
            ft.TextButton("تخطي - أكمل لاحقاً",on_click=lambda e: show_home()),
        ],scroll=ft.ScrollMode.AUTO))); page.update()
    def show_kyc_status():
        k=kyc_status(state["user_id"]); txt="قيد المراجعة" if k and k["status"]=="pending" else "تم التحقق ✅"
        page.controls.clear(); page.add(ft.Container(padding=20,content=ft.Column([
            ft.Text("حالة التحقق",size=24,weight="bold",color=GOLD), ft.Text(txt,size=16,color=ORANGE if k and k["status"]=="pending" else GREEN),
            ft.Text(f"{k['full_name'] if k else ''}\n{k['id_type'] if k else ''} - {k['id_number'] if k else ''}\nالميلاد: {k['dob'] if k else ''} - {k['birth_country'] if k else ''} - {k['birth_governorate'] if k else ''} - {k['birth_city'] if k else ''}",size=13,color=WHITE),
            ft.ElevatedButton("موافقة - دخول المحفظة (للعرض)",bgcolor=GREEN,color="white",width=400,on_click=lambda e: approve_demo()),
            ft.ElevatedButton("تعديل بياناتي",bgcolor=CARD,color=WHITE,width=400,on_click=lambda e: show_kyc()),
            ft.TextButton("خروج",on_click=lambda e: show_auth()),
        ]))); page.update()
    def show_home():
        page.controls.clear(); page.add(ft.Container(padding=16,content=ft.Column([
            ft.Row([ft.Text(f"أهلاً {state['name']}",size=20,weight="bold",color=WHITE), ft.TextButton("خروج",on_click=lambda e: show_auth())]),
            ft.Text("اسحب يمين / يسار - كل عملة بطاقة مستقلة",size=12,color=MUTED),
            home_cards, gold_label,
            ft.Text("كل المميزات - اضغط على أي خدمة للدخول",size=16,weight="bold",color=GOLD),
            ft.Row([ft.ElevatedButton("🇾🇪 شحن اليمن",bgcolor=CARD,color=WHITE,width=150,on_click=lambda e: show_services_cat("شحن جوال - اليمن")),
                    ft.ElevatedButton("🇸🇦 شحن السعودية",bgcolor=CARD,color=WHITE,width=150,on_click=lambda e: show_services_cat("شحن جوال - السعودية"))]),
            ft.Row([ft.ElevatedButton("🇦🇪 شحن الإمارات",bgcolor=CARD,color=WHITE,width=150,on_click=lambda e: show_services_cat("شحن جوال - الإمارات")),
                    ft.ElevatedButton("🇪🇬 شحن مصر",bgcolor=CARD,color=WHITE,width=150,on_click=lambda e: show_services_cat("شحن جوال - مصر"))]),
            ft.Row([ft.ElevatedButton("🌍 دول أخرى",bgcolor=CARD,color=WHITE,width=150,on_click=lambda e: show_services_cat("شحن جوال - دول أخرى")),
                    ft.ElevatedButton("💰 أسعار الذهب والعملات",bgcolor=CARD,color=WHITE,width=150,on_click=lambda e: show_gold_page())]),
            ft.Row([ft.ElevatedButton("💸 تحويل",bgcolor=GOLD,color="black",on_click=lambda e: show_transfer()),
                    ft.ElevatedButton("🛒 الخدمات والشحن",bgcolor=BLUE,color="white",on_click=lambda e: show_services()),
                    ft.ElevatedButton("🪪 KYC",bgcolor=CARD,color=WHITE,on_click=lambda e: show_kyc_status())]),
            ft.Text("السجل",size=16,weight="bold",color=GOLD), history_label,
            ft.Text("طلبات الخدمات",size=16,weight="bold",color=GOLD), orders_label,
            ft.Text("دعم 24/7: support@sultanwallet.com",size=11,color=MUTED)
        ]))); refresh_home()
    def show_transfer():
        page.controls.clear(); page.add(ft.Container(padding=20,content=ft.Column([
            ft.Text("تحويل",size=22,weight="bold",color=GOLD), transfer_type, to_f, amt_f, cur_dd,
            ft.ElevatedButton("تأكيد التحويل",bgcolor=GOLD,color="black",width=400,on_click=do_transfer),
            ft.ElevatedButton("رجوع",bgcolor=CARD,color=WHITE,width=400,on_click=lambda e: show_home()),
        ]))); page.update()
    def show_services():
        # build service cards
        def on_cat(cat):
            selected_cat["cat"]=cat; show_services()
        def on_pick(item):
            selected_service["item"]=item; show_services()
        cats=list(SERVICES.keys())
        cat_row=ft.Row(scroll=ft.ScrollMode.AUTO, controls=[ft.ElevatedButton(c, bgcolor=GOLD if c==selected_cat["cat"] else CARD, color="black" if c==selected_cat["cat"] else WHITE, on_click=lambda e, c=c: on_cat(c)) for c in cats])
        items=SERVICES[selected_cat["cat"]]
        item_cards=[]
        for it in items:
            sel = selected_service["item"] and selected_service["item"]["code"]==it["code"]
            item_cards.append(ft.Container(width=340, border_radius=14, bgcolor=GREEN if sel else CARD, padding=12, on_click=lambda e, it=it: on_pick(it), content=ft.Column([
                ft.Text(it["name"], size=15, weight="bold", color="black" if sel else WHITE),
                ft.Text(it["desc"], size=11, color="black" if sel else MUTED),
                ft.Text(f"السعر: {it['price']} {it['cur']}  •  كود: {it['code']}", size=12, weight="bold", color="black" if sel else GOLD),
                ft.Text("اضغط للاختيار ✅" if sel else "اضغط للاختيار", size=11, color="black" if sel else MUTED),
            ])))
        sel_txt = f"المختار: {selected_service['item']['name']} - {selected_service['item']['price']} {selected_service['item']['currency'] if 'currency' in selected_service['item'] else selected_service['item']['cur']}" if selected_service["item"] else "اختر خدمة من القائمة"
        # fix key: item uses cur
        if selected_service["item"]:
            sel_txt=f"المختار: {selected_service['item']['name']} - {selected_service['item']['price']} {selected_service['item']['cur']}"
        page.controls.clear()
        page.add(ft.Container(padding=16, content=ft.Column([
            ft.Text("الخدمات والشحن", size=22, weight="bold", color=GOLD),
            ft.Text("شحن جوال • انترنت • ألعاب • عملات تطبيقات • بطاقات • اشتراكات", size=13, color=MUTED),
            cat_row,
            ft.Text(f"عدد الخدمات في هذا القسم: {len(items)}", size=12, color=MUTED),
            ft.Column(item_cards, scroll=ft.ScrollMode.AUTO, height=320),
            ft.Text(sel_txt, size=14, weight="bold", color=GOLD),
            service_target, service_note,
            ft.ElevatedButton("تأكيد الشراء - خصم من المحفظة", bgcolor=GOLD, color="black", width=400, on_click=buy_service),
            ft.ElevatedButton("رجوع للرئيسية", bgcolor=CARD, color=WHITE, width=400, on_click=lambda e: show_home()),
            ft.Text("بعد الشراء يظهر الطلب في سجل الطلبات مع رقم مرجعي.", size=11, color=MUTED),
            ft.Text("طلباتي:", size=15, weight="bold", color=GOLD), ft.Text(orders_text(), size=12, color=WHITE),
        ], scroll=ft.ScrollMode.AUTO))); page.update()

    show_auth()
ft.app(target=main)
