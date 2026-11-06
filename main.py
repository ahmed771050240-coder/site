import os
import uuid
import flet as ft
import requests

API_URL = os.getenv(
    "SULTAN_WALLET_API_URL",
    "https://sultan-wallet-api.onrender.com"
).rstrip("/")


def api_request(method, endpoint, token=None, data=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.request(method, f"{API_URL}{endpoint}", json=data,
                                    headers=headers, timeout=25)
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        return response.status_code, payload
    except requests.RequestException:
        return 0, {"detail": "تعذر الاتصال بالخادم. تحقق من الإنترنت وحاول مجدداً."}


def main(page: ft.Page):
    page.title = "SULTAN WALLET"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B0F14"
    page.padding = 0
    page.rtl = True
    page.scroll = ft.ScrollMode.AUTO
    token = None
    user = None
    palette = {"bg": "#0B0F14", "card": "#151A23", "card2": "#1C2330",
               "green": "#10B981", "gold": "#D4AF37", "white": "#FFFFFF",
               "muted": "#8B95A5", "line": "#263041"}

    def message(msg):
        page.show_dialog(ft.AlertDialog(content=ft.Text(str(msg)), actions=[
            ft.TextButton("حسنًا", on_click=lambda e: page.pop_dialog())]))

    def text_field(label, password=False, keyboard=None):
        return ft.TextField(label=label, password=password, can_reveal_password=password,
                            keyboard_type=keyboard, border_color=palette["green"],
                            focused_border_color=palette["gold"], text_size=14)

    def card(content, padding=16):
        return ft.Container(content=content, padding=padding, bgcolor=palette["card"],
                            border=ft.Border.all(1, palette["line"]), border_radius=18)

    def title(text, subtitle=None):
        controls = [ft.Text(text, size=23, weight=ft.FontWeight.BOLD, color=palette["white"])]
        if subtitle:
            controls.append(ft.Text(subtitle, size=12, color=palette["muted"]))
        return ft.Column(controls, spacing=4)

    def api(method, path, data=None):
        return api_request(method, path, token, data)

    def fetch_wallet():
        status, result = api("GET", "/wallet")
        return result.get("accounts", []) if status == 200 else None

    def fetch_transactions(limit=50):
        status, result = api("GET", f"/wallet/transactions?limit={limit}")
        return result.get("transactions", []) if status == 200 else None

    def login_screen():
        page.navigation_bar = None
        phone = text_field("رقم الهاتف", keyboard=ft.KeyboardType.PHONE)
        password = text_field("كلمة المرور", True)
        def login(e):
            nonlocal token, user
            number, secret = (phone.value or "").strip(), password.value or ""
            if not number or not secret:
                message("أدخل رقم الهاتف وكلمة المرور")
                return
            status, result = api_request("POST", "/login", data={"phone": number, "password": secret})
            if status != 200 or not result.get("access_token"):
                message(result.get("detail", "تعذر تسجيل الدخول"))
                return
            token = result["access_token"]
            me_status, me = api_request("GET", "/me", token)
            if me_status != 200:
                token = None
                message(me.get("detail", "تعذر تحميل الحساب"))
                return
            user = me
            app_shell(0)
        def register_screen(e=None):
            register_page()
        page.controls.clear()
        page.add(ft.Container(expand=True, alignment=ft.Alignment.CENTER, padding=22,
            content=ft.Column([card(ft.Column([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=58, color=palette["gold"]),
                ft.Text("SULTAN WALLET", size=27, weight=ft.FontWeight.BOLD, color=palette["gold"]),
                ft.Text("محفظتك الرقمية... تحكم بثروتك بثقة", color=palette["muted"]),
                ft.Divider(color=palette["line"]), title("تسجيل الدخول", "أدخل بيانات حسابك للمتابعة"),
                phone, password,
                ft.Button("دخول آمن", width=320, on_click=login,
                          style=ft.ButtonStyle(bgcolor=palette["green"], color="#07110E")),
                ft.TextButton("إنشاء حساب جديد", on_click=register_screen),
                ft.Text("الدعم: ahmed771050240@gmail.com", size=11, color=palette["muted"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14), padding=22)],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)))
        page.update()

    def register_page():
        phone = text_field("رقم الهاتف", keyboard=ft.KeyboardType.PHONE)
        password = text_field("كلمة المرور (8 خانات على الأقل)", True)
        confirm = text_field("تأكيد كلمة المرور", True)
        def submit(e):
            number, secret = (phone.value or "").strip(), password.value or ""
            if len(number) < 7 or len(number) > 20 or len(secret) < 8 or secret != (confirm.value or ""):
                message("تحقق من رقم الهاتف وكلمة المرور وتأكيدها")
                return
            status, result = api_request("POST", "/register", data={"phone": number, "password": secret})
            if status in (200, 201):
                message("تم إنشاء الحساب. سجّل الدخول للمتابعة. توثيق الهاتف غير مفعّل حتى ربط مزود SMS.")
                login_screen()
            else:
                message(result.get("detail", "تعذر إنشاء الحساب"))
        page.controls.clear()
        page.add(ft.Container(expand=True, padding=22, alignment=ft.Alignment.CENTER,
            content=card(ft.Column([title("إنشاء حساب SULTAN WALLET"), phone, password, confirm,
                ft.Button("إنشاء الحساب", on_click=submit, width=320),
                ft.TextButton("العودة لتسجيل الدخول", on_click=lambda e: login_screen())],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14))))
        page.update()

    def show_home():
        accounts = fetch_wallet()
        transactions = fetch_transactions(6)
        wallet_unavailable = accounts is None
        if accounts is None:
            accounts = []
        balance_lines = [ft.Row([ft.Text(a.get("currency", ""), color=palette["muted"]),
            ft.Text(f'{a.get("balance", "0.00")} {a.get("currency", "")}',
                    color=palette["white"], weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN) for a in accounts]
        if not balance_lines:
            balance_lines = [ft.Text("تعذر تحميل الرصيد" if wallet_unavailable else "لا توجد أرصدة بعد", color=palette["muted"])]
        tx_rows = []
        for tx in (transactions or [])[:6]:
            incoming = tx.get("type") == "received"
            tx_rows.append(card(ft.Row([
                ft.Icon(ft.Icons.SOUTH_WEST if incoming else ft.Icons.NORTH_EAST,
                        color=palette["green"] if incoming else palette["gold"]),
                ft.Column([ft.Text("وارد" if incoming else "صادر", color=palette["white"]),
                           ft.Text(tx.get("description") or tx.get("status", ""), size=11, color=palette["muted"])], expand=True, spacing=2),
                ft.Text(f'{tx.get("amount", "0.00")} {tx.get("currency", "")}', color=palette["white"])
            ])))
        if not tx_rows:
            tx_rows = [card(ft.Text("لا توجد عمليات مسجلة", color=palette["muted"]))]
        page.controls.clear()
        page.add(ft.ListView(expand=True, padding=18, spacing=14, controls=[
            ft.Row([ft.Column([ft.Text("أهلاً بعودتك", color=palette["muted"], size=12),
                               ft.Text((user or {}).get("phone", "مستخدم"), color=palette["white"], size=16, weight=ft.FontWeight.BOLD)]),
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=34, color=palette["green"])],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            card(ft.Column([ft.Text("أرصدتك المتاحة", color=palette["muted"]), *balance_lines,
                ft.Divider(color=palette["line"]),
                ft.Text("رصيد المحفظة الداخلية فقط — لا يمثل أموالاً مودعة لدى بنك أو مزود دفع", color="#FBBF24", size=10)], spacing=9)),
            ft.Text("الخدمات", size=17, weight=ft.FontWeight.BOLD),
            ft.Row([ft.Button("تحويل", icon=ft.Icons.SEND, on_click=lambda e: app_shell(1)),
                    ft.OutlinedButton("سجل العمليات", icon=ft.Icons.RECEIPT_LONG, on_click=lambda e: app_shell(2))], wrap=True),
            ft.Text("آخر العمليات", size=17, weight=ft.FontWeight.BOLD), *tx_rows,
            ft.Text("SULTAN WALLET • مركز الحسابات", size=10, color=palette["muted"])
        ]))
        page.update()

    def transfer_page():
        recipient = text_field("رقم هاتف المستلم", keyboard=ft.KeyboardType.PHONE)
        amount = text_field("المبلغ")
        currency = ft.Dropdown(label="العملة", value="YER", options=[ft.dropdown.Option(x) for x in ("YER", "SAR", "AED", "USD")])
        note = text_field("وصف التحويل (اختياري)")
        transfer_key = str(uuid.uuid4())
        def submit(e):
            nonlocal transfer_key
            number, value = (recipient.value or "").strip(), (amount.value or "").strip()
            if not number or not value:
                message("أدخل رقم المستلم والمبلغ")
                return
            status, result = api("POST", "/wallet/transfers", {"recipient_phone": number,
                "amount": value, "currency": currency.value or "YER",
                "idempotency_key": transfer_key, "description": (note.value or "تحويل داخلي")[:200]})
            if status == 200 and result.get("status") == "completed":
                message(f'تم التحويل الداخلي. المرجع: {result.get("reference", "—")}')
                transfer_key = str(uuid.uuid4())
                app_shell(0)
            else:
                message(result.get("detail", "لم يتم تأكيد التحويل"))
        page.controls.clear()
        page.add(ft.ListView(expand=True, padding=18, spacing=14, controls=[title("تحويل بين المستخدمين", "تحويل داخلي من رصيدك المتاح فقط"),
            card(ft.Column([recipient, amount, currency, note,
                ft.Button("مراجعة وتنفيذ التحويل", icon=ft.Icons.SEND, on_click=submit,
                          style=ft.ButtonStyle(bgcolor=palette["green"], color="#07110E")),
                ft.Text("لن يتم خصم أي مبلغ إذا كان الرصيد غير كافٍ أو المستلم غير موجود. لا توجد حالياً تحويلات مصرفية خارجية.", size=11, color=palette["muted"])], spacing=12))]))
        page.update()

    def transactions_page():
        txs = fetch_transactions(100)
        controls = [title("سجل العمليات", "آخر 100 عملية مرتبطة بحسابك")]
        if txs is None:
            controls.append(card(ft.Text("تعذر تحميل سجل العمليات", color=palette["muted"])))
        elif not txs:
            controls.append(card(ft.Text("لا توجد عمليات حتى الآن", color=palette["muted"])))
        else:
            for tx in txs:
                incoming = tx.get("type") == "received"
                controls.append(card(ft.Column([
                    ft.Row([ft.Text("تحويل وارد" if incoming else "تحويل صادر", color=palette["white"], weight=ft.FontWeight.BOLD),
                             ft.Text(tx.get("status", ""), color=palette["green"])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f'{tx.get("amount", "0.00")} {tx.get("currency", "")}', size=18, color=palette["gold"]),
                    ft.Text(f'المرجع: {tx.get("reference", "—")}', size=10, color=palette["muted"]),
                    ft.Text(tx.get("description", ""), size=11, color=palette["muted"])
                ], spacing=5)))
        page.controls.clear(); page.add(ft.ListView(expand=True, padding=18, spacing=12, controls=controls)); page.update()

    def wallet_page():
        accounts = fetch_wallet()
        transactions = fetch_transactions(5)
        supported = ("YER", "SAR", "AED", "USD")
        by_currency = {a.get("currency"): a for a in (accounts or [])}
        controls = [
            ft.Row(
                [
                    title("محفظتي", "إدارة أرصدتك بالعملات المدعومة"),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="تحديث الأرصدة",
                        on_click=lambda e: wallet_page(),
                        icon_color=palette["gold"],
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        ]

        if accounts is None:
            controls.append(card(ft.Column([
                ft.Icon(ft.Icons.CLOUD_OFF, color=palette["gold"], size=30),
                ft.Text("تعذر تحميل أرصدة المحفظة", color=palette["white"], weight=ft.FontWeight.BOLD),
                ft.Text("تحقق من اتصال الإنترنت ثم حاول تحديث الصفحة.", color=palette["muted"], size=12),
                ft.OutlinedButton("إعادة المحاولة", icon=ft.Icons.REFRESH,
                                  on_click=lambda e: wallet_page()),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)))
        else:
            controls.append(card(ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=palette["gold"], size=25),
                    ft.Column([
                        ft.Text("محفظة SULTAN WALLET الداخلية", color=palette["white"], weight=ft.FontWeight.BOLD),
                        ft.Text(f'{len(accounts)} حسابات عملات مرتبطة بحسابك', color=palette["muted"], size=11),
                    ], expand=True, spacing=3),
                    ft.Container(content=ft.Text("متصلة", color=palette["green"], size=10),
                                 padding=8, bgcolor="#102D26", border_radius=20),
                ]),
                ft.Text("الأرصدة معروضة كلٌ بعملته؛ لا نجمع العملات المختلفة دون سعر صرف موثوق.",
                        color=palette["muted"], size=11),
            ], spacing=10)))

            currency_meta = {
                "YER": "ريال يمني",
                "SAR": "ريال سعودي",
                "AED": "درهم إماراتي",
                "USD": "دولار أمريكي",
            }
            for code in supported:
                account = by_currency.get(code)
                balance = account.get("balance", "0.00") if account else "0.00"
                status = account.get("status", "active") if account else "غير متاح"
                label = currency_meta[code]
                active = status == "active"
                controls.append(card(ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=palette["gold"], size=23),
                        width=46, height=46, alignment=ft.Alignment.CENTER,
                        bgcolor=palette["card2"], border_radius=14,
                    ),
                    ft.Column([
                        ft.Text(label, color=palette["white"], weight=ft.FontWeight.BOLD),
                        ft.Text(code + (" • نشطة" if active else " • " + str(status)),
                                color=palette["muted"], size=11),
                    ], expand=True, spacing=3),
                    ft.Column([
                        ft.Text(str(balance), color=palette["green"] if active else palette["muted"],
                                size=19, weight=ft.FontWeight.BOLD),
                        ft.Text(code, color=palette["muted"], size=10),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=1),
                ]), padding=14))

            controls.append(ft.Text("الخدمات السريعة", size=16, weight=ft.FontWeight.BOLD,
                                    color=palette["white"]))
            controls.append(ft.ResponsiveRow([
                ft.Container(col={"xs": 6, "sm": 3}, content=ft.Button(
                    "تحويل داخلي", icon=ft.Icons.SEND, expand=True,
                    on_click=lambda e: app_shell(1),
                    style=ft.ButtonStyle(bgcolor=palette["green"], color="#07110E"))),
                ft.Container(col={"xs": 6, "sm": 3}, content=ft.OutlinedButton(
                    "سجل العمليات", icon=ft.Icons.RECEIPT_LONG, expand=True,
                    on_click=lambda e: app_shell(2))),
            ], spacing=8, run_spacing=8))

            controls.append(card(ft.Column([
                ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE, color=palette["gold"]),
                        ft.Text("الإيداع والسحب", color=palette["white"], weight=ft.FontWeight.BOLD)]),
                ft.Text("سيتم تفعيل الإيداع والسحب بعد ربط مزود دفع مرخص وإكمال متطلبات التاجر والامتثال. أرصدة هذه النسخة داخلية ولا تمثل أموالاً مودعة لدى بنك.",
                        color=palette["muted"], size=11),
            ], spacing=8)))

            controls.append(ft.Text("آخر الحركات", size=16, weight=ft.FontWeight.BOLD,
                                    color=palette["white"]))
            if transactions is None:
                controls.append(card(ft.Text("تعذر تحميل آخر الحركات", color=palette["muted"])))
            elif not transactions:
                controls.append(card(ft.Text("لا توجد حركات مسجلة بعد", color=palette["muted"])))
            else:
                for tx in transactions:
                    incoming = tx.get("type") in ("received", "incoming")
                    controls.append(card(ft.Row([
                        ft.Icon(ft.Icons.SOUTH_WEST if incoming else ft.Icons.NORTH_EAST,
                                color=palette["green"] if incoming else palette["gold"]),
                        ft.Column([
                            ft.Text("تحويل وارد" if incoming else "تحويل صادر",
                                    color=palette["white"], size=12, weight=ft.FontWeight.BOLD),
                            ft.Text(tx.get("description") or tx.get("status", ""),
                                    color=palette["muted"], size=10),
                        ], expand=True, spacing=2),
                        ft.Text(f'{tx.get("amount", "0.00")} {tx.get("currency", "")}',
                                color=palette["white"], size=12),
                    ]), padding=12))

        page.controls.clear()
        page.add(ft.ListView(expand=True, padding=18, spacing=12, controls=controls))
        page.update()

    def settings_page():
        def logout(e):
            nonlocal token, user
            token, user = None, None
            login_screen()
        verified = bool((user or {}).get("phone_verified"))
        page.controls.clear()
        page.add(ft.ListView(expand=True, padding=18, spacing=12, controls=[title("الإعدادات والحساب"),
            card(ft.Column([ft.Text("بيانات الحساب", color=palette["white"], weight=ft.FontWeight.BOLD),
                ft.Text(f'رقم الهاتف: {(user or {}).get("phone", "—")}', color=palette["muted"]),
                ft.Text(f'رقم المستخدم: {(user or {}).get("id", "—")}', color=palette["muted"]),
                ft.Text("حالة الهاتف: موثّق" if verified else "حالة الهاتف: غير موثّق", color=palette["gold"])])),
            card(ft.Column([ft.Text("الأمان والخصوصية", color=palette["white"], weight=ft.FontWeight.BOLD),
                ft.Text("تشفير كلمات المرور وتوكن جلسة محدود المدة مفعّلان على الخادم. المصادقة الثنائية وKYC تحتاج مزود تحقق وربطاً تشغيلياً.", color=palette["muted"], size=12)])),
            card(ft.Column([ft.Text("الدعم الفني", color=palette["white"], weight=ft.FontWeight.BOLD),
                ft.Text("ahmed771050240@gmail.com", color=palette["muted"]),
                ft.Button("مراسلة الدعم", action=ft.OpenUrl("mailto:ahmed771050240@gmail.com"))])),
            ft.OutlinedButton("تسجيل الخروج", icon=ft.Icons.LOGOUT, on_click=logout)
        ])); page.update()

    def app_shell(index=0):
        destinations = [ft.NavigationBarDestination(icon=ft.Icons.HOME_ROUNDED, label="الرئيسية"),
                        ft.NavigationBarDestination(icon=ft.Icons.SEND, label="تحويل"),
                        ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG, label="العمليات"),
                        ft.NavigationBarDestination(icon=ft.Icons.WALLET_OUTLINED, label="المحفظة"),
                        ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="الإعدادات")]
        def navigate(e):
            i = e.control.selected_index
            [show_home, transfer_page, transactions_page, wallet_page, settings_page][i]()
        page.navigation_bar = ft.NavigationBar(destinations=destinations, selected_index=index,
            on_change=navigate, bgcolor=palette["card"], indicator_color="#174D3D")
        [show_home, transfer_page, transactions_page, wallet_page, settings_page][index]()
        page.update()

    login_screen()


ft.run(main)
