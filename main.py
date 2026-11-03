import flet as ft
import requests

API_URL = "https://sultan-wallet-api.onrender.com"


def api_post(endpoint, data, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            json=data,
            headers=headers,
            timeout=25,
        )
        try:
            result = response.json()
        except ValueError:
            result = {}
        return response.status_code, result
    except requests.RequestException:
        return 0, {"detail": "تعذر الاتصال بالخادم. تحقق من الإنترنت وحاول مجدداً."}


def api_get(endpoint, token):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=25,
        )
        try:
            result = response.json()
        except ValueError:
            result = {}
        return response.status_code, result
    except requests.RequestException:
        return 0, {"detail": "تعذر الاتصال بالخادم."}


def main(page: ft.Page):
    page.title = "Sultan Wallet"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#0B0F14"

    session_token = None
    current_user = None

    def show_message(message):
        page.show_dialog(
            ft.AlertDialog(
                content=ft.Text(message),
                actions=[
                    ft.TextButton(
                        "حسنًا",
                        on_click=lambda e: page.pop_dialog()
                    )
                ],
            )
        )


    def brand_header():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET,
                            size=58, color="#FFD700"),
                    ft.Text("SULTAN WALLET", size=27,
                            weight=ft.FontWeight.BOLD, color="#FFD700"),
                    ft.Text("محفظتك الرقمية... تحكم بثروتك بثقة",
                            size=15, color="#FFFFFF",
                            text_align=ft.TextAlign.CENTER),
                    ft.Divider(color="#66521A", height=12),
                    ft.Text("إدارة الحسابات • التحويلات • الخدمات المالية",
                            size=12, color="#D6C28A",
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("الأمان والوضوح وسهولة الاستخدام في مكان واحد",
                            size=12, color="#AAAAAA",
                            text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=9,
            ),
            width=420,
            padding=20,
            bgcolor="#181820",
            border=ft.Border.all(1, "#B99536"),
            border_radius=22,
        )

    def contact_panel():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("نحن هنا لمساعدتك", size=15,
                            weight=ft.FontWeight.BOLD, color="#FFD700"),
                    ft.Text("الدعم الرسمي للمحفظة",
                            size=12, color="#CCCCCC"),
                    ft.Text("ahmed771050240@gmail.com",
                            size=13, color="#FFFFFF"),
                    ft.Button(
                        "مراسلة الدعم عبر البريد الإلكتروني",
                        width=300,
                        style=ft.ButtonStyle(
                            bgcolor="#2A2A32", color="#FFD700"),
                        action=ft.OpenUrl(
                            "mailto:ahmed771050240@gmail.com"),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=7,
            ),
            padding=14,
            bgcolor="#181820",
            border=ft.Border.all(1, "#66521A"),
            border_radius=16,
        )

    def show_login_options(e=None):
        page.controls.clear()
        phone = ft.TextField(
            label="رقم الهاتف",
            keyboard_type=ft.KeyboardType.PHONE,
            border_color="#FFD700",
            width=300,
        )
        password = ft.TextField(
            label="كلمة المرور",
            password=True,
            can_reveal_password=True,
            border_color="#FFD700",
            width=300,
        )

        def show_register_screen(e=None):
            page.controls.clear()
            reg_phone = ft.TextField(
                label="رقم الهاتف",
                keyboard_type=ft.KeyboardType.PHONE,
                width=300,
            )
            reg_password = ft.TextField(
                label="كلمة المرور",
                password=True,
                can_reveal_password=True,
                width=300,
            )
            confirm_password = ft.TextField(
                label="تأكيد كلمة المرور",
                password=True,
                can_reveal_password=True,
                width=300,
            )

            def submit_registration(e):
                number = (reg_phone.value or "").strip()
                secret = reg_password.value or ""
                confirm = confirm_password.value or ""

                if not number or not secret or not confirm:
                    show_message("أكمل جميع البيانات.")
                    return
                if len(number) < 7 or len(number) > 20:
                    show_message("رقم الهاتف يجب أن يكون بين 7 و20 خانة.")
                    return
                if len(secret) < 8:
                    show_message("كلمة المرور يجب أن تكون 8 خانات على الأقل.")
                    return
                if secret != confirm:
                    show_message("كلمتا المرور غير متطابقتين.")
                    return

                status, result = api_post("/register", {
                    "phone": number,
                    "password": secret
                })
                if status in (200, 201):
                    show_message(
                        "تم إنشاء الحساب. رقم الهاتف غير موثق بعد؛ "
                        "يمكنك تسجيل الدخول، وسنضيف توثيق واتساب لاحقاً."
                    )
                else:
                    show_message(result.get("detail", "تعذر إنشاء الحساب."))

            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            brand_header(),
                            ft.Text(
                                "إنشاء حساب جديد",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="#FFD700",
                            ),
                            reg_phone,
                            reg_password,
                            confirm_password,
                            ft.Button(
                                "إنشاء الحساب",
                                width=300,
                                on_click=submit_registration,
                            ),
                            ft.TextButton(
                                "العودة إلى تسجيل الدخول",
                                on_click=show_login_options,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                    padding=20,
                )
            )
            page.update()

        def login_user(e):
            nonlocal session_token, current_user
            number = (phone.value or "").strip()
            secret = password.value or ""
            if not number or not secret:
                show_message("أدخل رقم الهاتف وكلمة المرور.")
                return
            status, result = api_post("/login", {
                "phone": number, "password": secret
            })
            if status == 200 and result.get("access_token"):
                token = result["access_token"]
                try:
                    r = requests.get(
                        f"{API_URL}/me",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=25
                    )
                    if r.status_code == 200:
                        session_token = token
                        current_user = r.json()
                        page.navigation_bar.visible = True
                        show_dashboard()
                    else:
                        show_message("تعذر تحميل بيانات الحساب.")
                except requests.RequestException:
                    show_message("تعذر الاتصال بالخادم.")
            else:
                show_message(result.get("detail", "فشل تسجيل الدخول."))

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        brand_header(),
                        ft.Text("مرحباً بعودتك", size=19,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF"),
                        ft.Icon(ft.Icons.LOCK, size=38, color="#FFD700"),
                        ft.Text("SULTAN WALLET", size=24,
                                weight=ft.FontWeight.BOLD, color="#FFD700"),
                        ft.Text("تسجيل الدخول", size=18, color="#FFFFFF"),
                        phone,
                        password,
                        ft.Button(
                            "دخول",
                            width=300,
                            style=ft.ButtonStyle(bgcolor="#FFD700", color="#0D0D11"),
                            on_click=login_user,
                        ),
                        ft.Text("ليس لديك حساب بالفعل؟", color="#FFFFFF"),
                        ft.TextButton(
                            "إنشاء حساب جديد",
                            on_click=show_register_screen,
                        ),
                        ft.Button(
                            "نسيت كلمة المرور؟",
                            width=300,
                            on_click=lambda e: show_message(
                                "استعادة كلمة المرور تحتاج خدمة تحقق آمنة."
                            ),
                        ),
                        contact_panel(),
                        ft.Button(
                            "المساعدة عبر واتساب",
                            width=300,
                            action=ft.OpenUrl("https://wa.me/967779599066"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=20,
            )
        )
        page.update()

    # ------------------ SULTAN WALLET — Emerald Dark UI ------------------
    UI = {
        "bg": "#0B0F14", "card": "#151A23", "card2": "#1C2330",
        "green": "#10B981", "green2": "#059669", "gold": "#D4AF37",
        "white": "#FFFFFF", "muted": "#8B95A5", "line": "#263041",
    }

    def get_dashboard():
        wallet_status, wallet_data = api_get("/wallet", session_token) if session_token else (0, {})
        tx_status, tx_data = api_get("/wallet/transactions?limit=10", session_token) if session_token else (0, {})
        accounts = wallet_data.get("accounts", []) if isinstance(wallet_data, dict) else []
        transactions = tx_data.get("transactions", []) if isinstance(tx_data, dict) else []
        balance_summary = "   •   ".join(
            f"{a.get('balance', '0.00')} {a.get('currency', '')}" for a in accounts
        ) or ("تعذر تحميل الأرصدة" if wallet_status != 200 else "لا توجد أرصدة مسجلة بعد")
        user_phone = current_user.get("phone", "مستخدم") if current_user else "مستخدم"
        user_id = current_user.get("id", "—") if current_user else "—"
        verified = "موثّق" if current_user and current_user.get("phone_verified") else "غير موثّق"

        def section_title(title, trailing=None):
            controls = [ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=UI["white"])]
            if trailing:
                controls.append(ft.Text(trailing, size=11, color=UI["muted"]))
            return ft.Row(controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        def quick_action(icon, title, message, primary=False):
            return ft.Column([
                ft.Container(
                    content=ft.Icon(icon, color=UI["white"] if primary else UI["green"], size=21),
                    width=56, height=56,
                    bgcolor=UI["green"] if primary else UI["card"],
                    border_radius=18, alignment=ft.Alignment.CENTER,
                    border=None if primary else ft.Border.all(1, UI["line"]),
                    on_click=lambda e: show_message(message),
                ),
                ft.Text(title, size=11, color=UI["white"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=7)

        tx_controls = []
        if transactions:
            for tx in transactions[:8]:
                amount = str(tx.get("amount", "0.00"))
                currency = str(tx.get("currency", ""))
                tx_type = str(tx.get("type", "عملية"))
                tx_status_text = str(tx.get("status", ""))
                tx_controls.append(ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Icon(ft.Icons.SWAP_HORIZ, color=UI["green"], size=20),
                                     width=42, height=42, bgcolor=UI["card2"], border_radius=13,
                                     alignment=ft.Alignment.CENTER),
                        ft.Column([
                            ft.Text(tx_type, color=UI["white"], size=12, weight=ft.FontWeight.BOLD),
                            ft.Text(tx_status_text, color=UI["muted"], size=10),
                        ], spacing=3, expand=True),
                        ft.Text(f"{amount} {currency}", color=UI["white"], size=12,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=10),
                    padding=12, bgcolor=UI["card"], border_radius=14,
                ))
        else:
            tx_controls.append(ft.Container(
                content=ft.Text("لا توجد عمليات مسجلة حتى الآن" if tx_status == 200 else "تعذر تحميل العمليات حالياً",
                                color=UI["muted"], size=12),
                padding=16, bgcolor=UI["card"], border_radius=14,
            ))

        return ft.ListView(
            expand=True, padding=ft.padding.symmetric(horizontal=18, vertical=18), spacing=15,
            controls=[
                ft.Row([
                    ft.Row([
                        ft.CircleAvatar(content=ft.Text("س", color=UI["white"]), bgcolor=UI["card2"], radius=21),
                        ft.Column([
                            ft.Text("أهلاً بعودتك", color=UI["muted"], size=11),
                            ft.Text(user_phone, color=UI["white"], size=14, weight=ft.FontWeight.BOLD),
                        ], spacing=2),
                    ], spacing=10),
                    ft.Container(content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE, color=UI["white"], size=21),
                                 width=42, height=42, bgcolor=UI["card"], border_radius=14,
                                 alignment=ft.Alignment.CENTER),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("الرصيد الكلي", color="#FFFFFFB0", size=13),
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=UI["green"], size=20),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(balance_summary, color=UI["white"], size=23, weight=ft.FontWeight.BOLD),
                        ft.Text("أرصدة الحساب الداخلية", color=UI["muted"], size=11),
                        ft.Divider(color=UI["line"], height=18),
                        ft.Row([
                            ft.Column([ft.Text("الحساب", color=UI["muted"], size=10), ft.Text(str(user_id), color=UI["white"], size=12)] , spacing=3),
                            ft.Column([ft.Text("حالة الهاتف", color=UI["muted"], size=10), ft.Text(verified, color=UI["green"], size=12)] , spacing=3),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text("الإيداع والسحب والتحويلات المالية غير مفعّلة حالياً", color="#FBBF24", size=10),
                    ], spacing=7),
                    padding=19, border_radius=23,
                    gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                                               colors=["#1A2C35", "#111827", "#0F172A"]),
                    border=ft.Border.all(1, "#245044"),
                ),
                section_title("الخدمات السريعة"),
                ft.Row([
                    quick_action(ft.Icons.SEND_ROUNDED, "تحويل", "التحويل غير مفعّل حالياً." , True),
                    quick_action(ft.Icons.ADD_CARD, "شحن", "الإيداع غير مفعّل حالياً."),
                    quick_action(ft.Icons.MONEY, "سحب", "السحب غير مفعّل حالياً."),
                    quick_action(ft.Icons.RECEIPT_LONG, "كشف حساب", "التقارير غير متاحة حالياً."),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                section_title("بطاقاتي", "SULTAN WALLET"),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("SULTAN WALLET", color=UI["white"], size=11, weight=ft.FontWeight.BOLD),
                                ft.Icon(ft.Icons.WIFI, color=UI["white"], size=17)],
                               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=10),
                        ft.Text("••••  ••••  ••••  0087", color=UI["white"], size=17, weight=ft.FontWeight.BOLD),
                        ft.Text("DIGITAL WALLET", color="#FFFFFF99", size=9),
                    ], spacing=5),
                    padding=18, height=118, border_radius=18,
                    gradient=ft.LinearGradient(colors=["#0F172A", UI["green2"]]),
                ),
                section_title("العمليات الأخيرة", "آخر 10 عمليات"),
                ft.Column(tx_controls, spacing=9),
                ft.Container(height=20),
            ],
        )

    def show_dashboard():
        page.controls.clear()
        page.add(get_dashboard())
        page.update()

    def handle_navigation(e):
        index = e.control.selected_index
        page.controls.clear()

        if index == 0:
            page.add(get_dashboard())
        else:
            titles = {
                1: "المحفظة",
                2: "الإحصائيات",
                3: "الإعدادات",
            }
            descriptions = {
                1: "تفاصيل أرصدة محفظتك تظهر في الرئيسية حالياً.",
                2: "قسم الإحصائيات قيد التجهيز.",
                3: "إعدادات الحساب قيد التجهيز.",
            }
            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                [ft.Icons.WALLET_OUTLINED, ft.Icons.BAR_CHART, ft.Icons.SETTINGS][index - 1],
                                size=55,
                                color="#10B981",
                            ),
                            ft.Text(
                                titles[index],
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="#10B981",
                            ),
                            ft.Text(descriptions[index], color="#FFFFFF"),
                            ft.Button(
                                "العودة للرئيسية",
                                on_click=lambda e: show_dashboard(),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                )
            )

        page.update()

    # شريط التنقل السفلي
    page.navigation_bar = ft.NavigationBar(
        visible=False,
        bgcolor="#151A23",
        selected_index=0,
        on_change=handle_navigation,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_ROUNDED, label="الرئيسية"),
            ft.NavigationBarDestination(icon=ft.Icons.WALLET_OUTLINED, label="المحفظة"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="الإحصائيات"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, label="الإعدادات"),
        ]
    )

    show_login_options()

ft.run(main)
