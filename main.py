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
    page.bgcolor = "#0D0D11"

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

    # ------------------ 2. لوحة التحكم والإحصائيات والواجهة الملكية ------------------
    def get_dashboard():
        wallet_data = {}
        wallet_error = False
        if session_token:
            wallet_status, wallet_data = api_get("/wallet", session_token)
            wallet_error = wallet_status != 200
        transactions_data = {}
        transactions_error = False
        if session_token:
            tx_status, transactions_data = api_get("/wallet/transactions?limit=10", session_token)
            transactions_error = tx_status != 200
        transactions = transactions_data.get("transactions", []) if isinstance(transactions_data, dict) else []
        accounts = wallet_data.get("accounts", []) if isinstance(wallet_data, dict) else []
        wallet_summary = " | ".join(
            str(a.get("currency", "")) + ": " + str(a.get("balance", "0.00"))
            for a in accounts
        ) or ("تعذر جلب الأرصدة" if wallet_error else "لا توجد أرصدة داخلية بعد")
        transaction_text = "\n".join([str(t.get("type", "عملية")) + " | " + str(t.get("amount", "0.00")) + " " + str(t.get("currency", "")) + " | " + str(t.get("status", "")) for t in transactions]) or "لا توجد عمليات مسجلة حتى الآن" if not transactions_error else "تعذر تحميل العمليات"; return ft.ListView(
            padding=20,
            controls=[
                # الهيدر الترحيبي
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("مرحباً بك 👋 " + (current_user.get("phone", "مستخدم") if current_user else "مستخدم"), size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            ft.Text("Sultan Wallet - الحساب الملكي", size=12, color="#FFD700")
                        ]),
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color="#0D0D11"),
                            bgcolor="#FFD700",
                            radius=22
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(height=25, color=ft.Colors.TRANSPARENT),

                # بيانات الحساب الحقيقية
                ft.Container(
                    content=ft.Column([
                        ft.Text("بيانات الحساب 👤", size=16, weight=ft.FontWeight.BOLD, color="#FFD700"),
                        ft.Text("رقم الحساب: " + str(current_user.get("id", "غير متاح") if current_user else "غير متاح"), color="#FFFFFF"),
                        ft.Text("رقم الهاتف: " + str(current_user.get("phone", "غير متاح") if current_user else "غير متاح"), color="#FFFFFF"),
                        ft.Text("توثيق الهاتف: " + ("موثّق" if current_user and current_user.get("phone_verified") else "غير موثّق"), color="#FFFFFF"),
                        ft.Text("تاريخ إنشاء الحساب: " + str(current_user.get("created_at", "غير متاح") if current_user else "غير متاح"), color="#FFFFFF"),
                    ], spacing=10),
                    padding=18,
                    bgcolor="#181820",
                    border_radius=15,
                    border=ft.Border.all(1, "#FFD700")
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

                # صورة SULTAN WALLET الترويجية
                ft.Container(
                    content=ft.Image(
                        src="sultan_wallet_promo.webp",
                        width=340,
                        height=170,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    padding=8,
                    bgcolor="#181820",
                    border_radius=18,
                    border=ft.Border.all(1, "#FFD700"),
                ),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),

                # بطاقة الرصيد الفخمة
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("الرصيد الكلي المتاح", color="#DDDDDD", size=14),
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color="#FFD700")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text("أرصدة المحفظة الداخلية", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        ft.Text(wallet_summary, size=16, color="#FFD700"),
                        ft.Text("الأموال الحقيقية والإيداع والسحب غير مفعّلة حالياً", size=12, color="#DDDDDD"),
                        ft.Divider(height=10, color="#333333"),
                        ft.Row([
                            ft.Row([ft.Icon(ft.Icons.ARROW_UPWARD, color="#00FF7F", size=16), ft.Text("الدخل: لا توجد بيانات", color="#00FF7F", size=12)]),
                            ft.Row([ft.Icon(ft.Icons.ARROW_DOWNWARD, color="#FF4500", size=16), ft.Text("المصروف: لا توجد بيانات", color="#FF4500", size=12)])
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]),
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1, -1),
                        end=ft.Alignment(1, 1),
                        colors=["#1E1E26", "#2D2D3A", "#141419"]
                    ),
                    padding=20,
                    border_radius=20,
                    border=ft.Border.all(1, "#FFD700")
                ),
                ft.Divider(height=25, color=ft.Colors.TRANSPARENT),

                # 3. قسم الإحصائيات والرسوم البيانية التفاعلية
                ft.Text("آخر العمليات المالية 📋", size=17, weight=ft.FontWeight.BOLD, color="#FFD700"),
                ft.Text(transaction_text, color="#FFFFFF", size=13),
                ft.Text("إحصائيات المصروفات والنمو 📊", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("استهلاك الميزانية الشهرية", color="#AAAAAA"), ft.Text("--", color="#FFD700")]),
                        ft.ProgressBar(value=0.0, color="#FFD700", bgcolor="#333333", height=10),
                        ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                        ft.Row([
                            ft.Column([ft.Text("الأرباح", size=12, color="#888888"), ft.Text("غير متاح", color="#00FF7F", weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("الاستثمار", size=12, color="#888888"), ft.Text("غير متاح", color="#FFD700", weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("الأمان", size=12, color="#888888"), ft.Text("غير مفعل", color="#00E5FF", weight=ft.FontWeight.BOLD)])
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
                    ]),
                    padding=15,
                    bgcolor="#181820",
                    border_radius=15
                ),
                ft.Divider(height=25, color=ft.Colors.TRANSPARENT),

                # أزرار العمليات السريعة
                ft.Text("الخدمات السريعة ⚡", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Row([
                    ft.Button("إرسال أموال 💸", style=ft.ButtonStyle(bgcolor="#FFD700", color="#000000"), on_click=lambda e: show_message("التحويل غير مفعّل حالياً.")),
                    ft.Button("تعبئة رصيد 💳", style=ft.ButtonStyle(bgcolor="#2D2D3A", color="#FFFFFF"), on_click=lambda e: show_message("الإيداع غير مفعّل حالياً.")),
                    ft.Button("تقرير PDF 📄", style=ft.ButtonStyle(bgcolor="#2D2D3A", color="#FFD700"), on_click=lambda e: show_message("التقارير غير متاحة حالياً."))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]
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
                1: "الإحصائيات",
                2: "الأمان",
                3: "الإعدادات",
            }
            descriptions = {
                1: "قسم الإحصائيات قيد التجهيز.",
                2: "إعدادات الأمان قيد التجهيز.",
                3: "إعدادات الحساب قيد التجهيز.",
            }
            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                [ft.Icons.BAR_CHART, ft.Icons.SECURITY, ft.Icons.SETTINGS][index - 1],
                                size=55,
                                color="#FFD700",
                            ),
                            ft.Text(
                                titles[index],
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="#FFD700",
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
        bgcolor="#141419",
        selected_index=0,
        on_change=handle_navigation,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="الرئيسية"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="الإحصائيات"),
            ft.NavigationBarDestination(icon=ft.Icons.SECURITY, label="الأمان"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="الإعدادات"),
        ]
    )

    show_login_options()

ft.run(main)
