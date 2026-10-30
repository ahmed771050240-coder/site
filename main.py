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

def main(page: ft.Page):
    page.title = "Sultan Wallet"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#0D0D11"

    session_token = None
    current_user = None

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

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.LOCK, size=65, color="#FFD700"),
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
        return ft.ListView(
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

                # بطاقة الرصيد الفخمة
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("الرصيد الكلي المتاح", color="#DDDDDD", size=14),
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color="#FFD700")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text("الحساب غير مفعّل مالياً", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
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
                    border=ft.border.all(1, "#FFD700")
                ),
                ft.Divider(height=25, color=ft.Colors.TRANSPARENT),

                # 3. قسم الإحصائيات والرسوم البيانية التفاعلية
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

    # شريط التنقل السفلي الفخم
    page.navigation_bar = ft.NavigationBar(
        visible=False,
        bgcolor="#141419",
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="الرئيسية"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="الإحصائيات"),
            ft.NavigationBarDestination(icon=ft.Icons.SECURITY, label="الأمان"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="الإعدادات"),
        ]
    )

    show_login_options()

ft.run(main)
