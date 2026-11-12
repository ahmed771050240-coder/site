"""SULTAN WALLET — professional client shell.

The client never stores or creates financial balances. All account data is read
from the authenticated HTTPS API. Unsupported regulated features are visibly
marked unavailable rather than simulated.
"""
import os
import flet as ft
from wallet_api import WalletAPI, WalletAPIError

API_BASE_URL = os.environ.get(
    "SULTAN_WALLET_API_URL",
    "https://sultan-wallet-api.onrender.com",
).rstrip("/")

BG = "#080D18"
PANEL = "#111B2E"
PANEL_ALT = "#17243A"
GOLD = "#D4AF37"
GOLD_LIGHT = "#F2D477"
WHITE = "#F8FAFC"
MUTED = "#94A3B8"
GREEN = "#10B981"
RED = "#EF4444"


def main(page: ft.Page):
    api = WalletAPI(API_BASE_URL)
    state = {
        "token": None,
        "profile": None,
        "wallets": [],
        "capabilities": {},
        "screen": 0,
        "hide_balances": False,
    }

    page.title = "SULTAN WALLET"
    page.bgcolor = BG
    page.padding = 0
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK

    def notify(message):
        try:
            page.show_dialog(
                ft.SnackBar(content=ft.Text(str(message)), bgcolor=PANEL_ALT)
            )
        except Exception:
            print(str(message))

    def load_account(token):
        profile = api.me(token)
        wallet_result = api.wallets(token)
        capabilities = api.capabilities()
        state["token"] = token
        state["profile"] = profile
        state["wallets"] = wallet_result.get("wallets", [])
        state["capabilities"] = capabilities
        return profile

    def auth_screen():
        page.navigation_bar = None
        page.appbar = None
        name_field = ft.TextField(
            label="الاسم الكامل",
            border_color=GOLD,
            text_size=15,
        )
        phone_field = ft.TextField(
            label="رقم الهاتف مع مفتاح الدولة",
            hint_text="+967 أو +966 أو +971",
            keyboard_type=ft.KeyboardType.PHONE,
            border_color=GOLD,
        )
        password_field = ft.TextField(
            label="كلمة المرور",
            password=True,
            can_reveal_password=True,
            border_color=GOLD,
        )
        status = ft.Text(
            "سجّل الدخول أو أنشئ حساباً للاتصال الآمن بالخادم",
            color=MUTED,
            size=12,
            text_align=ft.TextAlign.CENTER,
        )
        login_button = ft.Button(
            "تسجيل الدخول",
            icon=ft.Icons.LOGIN,
            bgcolor=GOLD,
            color="#111111",
            expand=True,
        )
        register_button = ft.Button(
            "إنشاء حساب",
            icon=ft.Icons.PERSON_ADD,
            bgcolor=PANEL_ALT,
            color=WHITE,
            expand=True,
        )

        def submit(mode):
            phone = (phone_field.value or "").strip()
            password = password_field.value or ""
            full_name = (name_field.value or "").strip()

            if not phone or not password:
                status.value = "أدخل رقم الهاتف وكلمة المرور"
                page.update()
                return
            if mode == "register":
                if len(full_name) < 2:
                    status.value = "أدخل الاسم الكامل"
                    page.update()
                    return
                if len(password) < 12:
                    status.value = "كلمة المرور يجب أن تكون 12 حرفاً على الأقل"
                    page.update()
                    return

            login_button.disabled = True
            register_button.disabled = True
            status.value = "جارٍ الاتصال بالخادم الآمن..."
            page.update()
            try:
                result = (
                    api.register(phone, full_name, password)
                    if mode == "register"
                    else api.login(phone, password)
                )
                token = result.get("access_token")
                if not token:
                    raise WalletAPIError("الخادم لم يُرجع رمز جلسة صالحاً")
                load_account(token)
                app_screen()
            except WalletAPIError as exc:
                status.value = str(exc)
                login_button.disabled = False
                register_button.disabled = False
                page.update()
            except Exception:
                status.value = "تعذر إكمال الطلب. تحقق من اتصال الخادم وحاول مجدداً."
                login_button.disabled = False
                register_button.disabled = False
                page.update()

        login_button.on_click = lambda e: submit("login")
        register_button.on_click = lambda e: submit("register")

        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                padding=22,
                content=ft.Container(
                    width=520,
                    padding=22,
                    border_radius=24,
                    bgcolor=PANEL,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16,
                        controls=[
                            ft.Icon(
                                ft.Icons.ACCOUNT_BALANCE_WALLET,
                                size=58,
                                color=GOLD,
                            ),
                            ft.Text(
                                "SULTAN WALLET",
                                size=27,
                                weight=ft.FontWeight.BOLD,
                                color=GOLD,
                            ),
                            ft.Text(
                                "محفظة متعددة العملات — اليمن والسعودية والإمارات",
                                size=13,
                                color=MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("YER", color=GOLD),
                                    ft.Text("• SAR • AED • USD", color=MUTED),
                                ],
                            ),
                            name_field,
                            phone_field,
                            password_field,
                            ft.Row(controls=[login_button, register_button]),
                            status,
                            ft.Text(
                                "الأرصدة المعروضة حسابات تجريبية على الخادم. "
                                "الإيداع والسحب والتحويلات والبطاقات غير مفعّلة "
                                "حتى اكتمال اعتماد وربط مزودي الخدمات المالية.",
                                size=11,
                                color=MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                ),
            )
        )
        page.update()

    def refresh_account():
        token = state.get("token")
        if not token:
            auth_screen()
            return
        try:
            load_account(token)
            render_screen()
        except WalletAPIError as exc:
            notify(exc)
        except Exception:
            notify("تعذر تحديث بيانات الحساب من الخادم")

    def title_bar(title):
        profile = state.get("profile") or {}
        return ft.Container(
            padding=16,
            bgcolor=PANEL,
            border_radius=18,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "SULTAN WALLET",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=GOLD,
                            ),
                            ft.Text(title, size=12, color=MUTED),
                        ],
                    ),
                    ft.Text(
                        profile.get("full_name", ""),
                        size=12,
                        color=WHITE,
                    ),
                ],
            ),
        )

    def money_text(value, currency):
        if state["hide_balances"]:
            return "••••••"
        return f"{value} {currency}"

    def wallet_tile(item):
        currency = item.get("currency", "—")
        balance = item.get("balance", "0.00")
        status_value = item.get("status", "unknown")
        return ft.Container(
            padding=16,
            border_radius=16,
            bgcolor=PANEL,
            border=ft.Border.all(1, "#263650"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=5,
                        controls=[
                            ft.Text(
                                currency,
                                size=17,
                                weight=ft.FontWeight.BOLD,
                                color=GOLD_LIGHT,
                            ),
                            ft.Text(
                                "حساب متعدد العملات",
                                size=11,
                                color=MUTED,
                            ),
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=5,
                        controls=[
                            ft.Text(
                                money_text(balance, currency),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=WHITE,
                            ),
                            ft.Text(
                                "تجريبي" if status_value == "demo" else status_value,
                                size=11,
                                color=MUTED,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def home_screen():
        profile = state.get("profile") or {}
        wallets = state.get("wallets") or []
        return ft.Column(
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                title_bar("الرئيسية"),
                ft.Container(
                    padding=20,
                    border_radius=20,
                    bgcolor=PANEL_ALT,
                    border=ft.Border.all(1, "#6C5924"),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("حسابك في سلطان واليت", color=MUTED),
                                    ft.IconButton(
                                        ft.Icons.VISIBILITY_OFF
                                        if state["hide_balances"]
                                        else ft.Icons.VISIBILITY,
                                        icon_color=GOLD,
                                        on_click=toggle_balances,
                                    ),
                                ],
                            ),
                            ft.Text(
                                profile.get("full_name", "مرحباً"),
                                size=23,
                                weight=ft.FontWeight.BOLD,
                                color=WHITE,
                            ),
                            ft.Text(
                                "الأرصدة مفصولة حسب العملة ولا يتم جمعها دون سعر صرف موثوق.",
                                size=11,
                                color=MUTED,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Button(
                                        "تحديث البيانات",
                                        icon=ft.Icons.REFRESH,
                                        bgcolor=GOLD,
                                        color="#111111",
                                        on_click=lambda e: refresh_account(),
                                    ),
                                    ft.Button(
                                        "الملف الشخصي",
                                        icon=ft.Icons.PERSON,
                                        bgcolor=PANEL,
                                        color=WHITE,
                                        on_click=lambda e: go_screen(4),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Text(
                    "ملخص المحافظ",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=GOLD,
                ),
                *([wallet_tile(item) for item in wallets] or [
                    ft.Text("لا توجد حسابات عملات متاحة حالياً.", color=MUTED)
                ]),
                ft.Container(
                    padding=14,
                    border_radius=14,
                    bgcolor="#192536",
                    content=ft.Text(
                        "حالة المنصة: حسابات عرض تجريبية. لا توجد أموال حقيقية "
                        "ولا يمكن تنفيذ حركة مالية حالياً.",
                        color=MUTED,
                        size=12,
                    ),
                ),
            ],
        )

    def wallets_screen():
        wallets = state.get("wallets") or []
        return ft.Column(
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                title_bar("المحافظ والعملات"),
                ft.Text(
                    "كل عملة لها حساب مستقل. الرصيد يأتي من الخادم فقط.",
                    size=12,
                    color=MUTED,
                ),
                *([wallet_tile(item) for item in wallets] or [
                    ft.Text("لم يُرجع الخادم حسابات بعد.", color=MUTED)
                ]),
                ft.Text(
                    "العملات المدعومة في بنية الحساب: YER • SAR • AED • USD",
                    size=12,
                    color=GOLD_LIGHT,
                ),
            ],
        )

    def transfers_screen():
        return ft.Column(
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                title_bar("التحويلات"),
                ft.Icon(ft.Icons.LOCK, size=42, color=GOLD),
                ft.Text(
                    "التحويلات غير مفعّلة حالياً",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=WHITE,
                ),
                ft.Text(
                    "لن نعرض زر تحويل يوهمك بأن الأموال تنتقل. "
                    "يلزم استكمال دفتر أستاذ مزدوج القيد، ومراجعة الأمان، "
                    "وربط مزود تحويل مرخص واختبار التسوية قبل تشغيل هذه الخدمة.",
                    color=MUTED,
                    size=13,
                ),
                ft.Container(
                    padding=16,
                    bgcolor=PANEL,
                    border_radius=14,
                    content=ft.Text(
                        "الحالة التقنية: واجهة التحويل قيد التجهيز — "
                        "لا يوجد مسار تحويل مالي منشور في API الحالي.",
                        color=GOLD_LIGHT,
                        size=12,
                    ),
                ),
            ],
        )

    def activity_screen():
        return ft.Column(
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                title_bar("سجل العمليات"),
                ft.Icon(ft.Icons.RECEIPT, size=42, color=GOLD),
                ft.Text(
                    "لا توجد عمليات مسجلة",
                    size=19,
                    weight=ft.FontWeight.BOLD,
                    color=WHITE,
                ),
                ft.Text(
                    "سجل العمليات سيظهر هنا بعد إضافة دفتر الأستاذ "
                    "ومسارات العمليات المعتمدة على الخادم. لا نعرض "
                    "حركات وهمية أو بيانات ثابتة.",
                    color=MUTED,
                    size=13,
                ),
            ],
        )

    def profile_screen():
        profile = state.get("profile") or {}
        caps = state.get("capabilities") or {}
        rows = [
            ("الاسم", profile.get("full_name", "—")),
            ("رقم الهاتف", profile.get("phone", "—")),
            ("حالة الحساب", profile.get("status", "—")),
            ("التحقق من الهوية KYC", "غير مربوط بعد"),
            ("التحقق الثنائي 2FA", "غير مفعّل"),
        ]
        return ft.Column(
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                title_bar("الملف الشخصي والأمان"),
                *[
                    ft.Container(
                        padding=13,
                        bgcolor=PANEL,
                        border_radius=12,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(label, color=MUTED, size=12),
                                ft.Text(value, color=WHITE, size=12),
                            ],
                        ),
                    )
                    for label, value in rows
                ],
                ft.Text(
                    "حالة مزايا المنصة",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=GOLD,
                ),
                *[
                    ft.Container(
                        padding=12,
                        bgcolor=PANEL,
                        border_radius=12,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(label, color=WHITE, size=12),
                                ft.Text(
                                    "متاح تقنياً" if enabled else "غير مفعّل",
                                    color=GREEN if enabled else MUTED,
                                    size=12,
                                ),
                            ],
                        ),
                    )
                    for label, enabled in [
                        ("التسجيل والدخول", caps.get("authentication", False)),
                        ("قراءة المحافظ", caps.get("wallet_read", False)),
                        ("الإيداع", caps.get("deposits", False)),
                        ("السحب", caps.get("withdrawals", False)),
                        ("التحويلات", caps.get("transfers", False)),
                        ("إصدار البطاقات", caps.get("card_issuing", False)),
                        ("تنفيذ الخدمات", caps.get("service_fulfillment", False)),
                    ]
                ],
                ft.Button(
                    "تحديث بيانات الحساب",
                    icon=ft.Icons.REFRESH,
                    bgcolor=PANEL_ALT,
                    color=WHITE,
                    on_click=lambda e: refresh_account(),
                ),
                ft.Button(
                    "تسجيل الخروج",
                    icon=ft.Icons.LOGOUT,
                    bgcolor="#5B2028",
                    color=WHITE,
                    on_click=lambda e: logout(),
                ),
            ],
        )

    def toggle_balances(e):
        state["hide_balances"] = not state["hide_balances"]
        render_screen()

    def go_screen(index):
        state["screen"] = index
        render_screen()

    def logout():
        state.update(
            token=None,
            profile=None,
            wallets=[],
            capabilities={},
            screen=0,
        )
        auth_screen()

    def render_screen():
        index = state["screen"]
        screens = [
            home_screen,
            wallets_screen,
            transfers_screen,
            activity_screen,
            profile_screen,
        ]
        labels = ["الرئيسية", "المحافظ", "التحويلات", "السجل", "حسابي"]
        icons = [
            ft.Icons.HOME_OUTLINED,
            ft.Icons.ACCOUNT_BALANCE_WALLET,
            ft.Icons.SEND,
            ft.Icons.HISTORY,
            ft.Icons.PERSON,
        ]
        page.controls.clear()
        page.appbar = None
        page.navigation_bar = ft.NavigationBar(
            bgcolor=PANEL,
            selected_index=index,
            on_change=lambda e: go_screen(e.control.selected_index),
            destinations=[
                ft.NavigationBarDestination(icon=icons[i], label=labels[i])
                for i in range(len(labels))
            ],
        )
        page.add(
            ft.Container(
                expand=True,
                padding=16,
                bgcolor=BG,
                content=screens[index](),
            )
        )
        page.update()

    def app_screen():
        state["screen"] = 0
        render_screen()

    auth_screen()


if __name__ == "__main__":
    ft.run(main)
