import flet as ft
import secrets
from wallet_api import WalletAPI

CURRENCIES = [
    {"code": "USD", "name": "دولار أمريكي", "flag": "🇺🇸", "rate": 1650, "change": 0.8, "fav": True},
    {"code": "SAR", "name": "ريال سعودي", "flag": "🇸🇦", "rate": 440, "change": -0.4, "fav": True},
    {"code": "AED", "name": "درهم إماراتي", "flag": "🇦🇪", "rate": 449, "change": 0.2, "fav": True},
    {"code": "EGP", "name": "جنيه مصري", "flag": "🇪🇬", "rate": 34, "change": 0.3, "fav": False},
    {"code": "INR", "name": "روبية هندية", "flag": "🇮🇳", "rate": 20, "change": 0.1, "fav": False},
    {"code": "CNY", "name": "يوان صيني", "flag": "🇨🇳", "rate": 228, "change": 0.5, "fav": False},
    {"code": "JPY", "name": "ين ياباني", "flag": "🇯🇵", "rate": 11, "change": -0.2, "fav": False},
    {"code": "GBP", "name": "جنيه إسترليني", "flag": "🇬🇧", "rate": 2090, "change": 0.6, "fav": False},
]

GOLD = [
    {"name": "ذهب عيار 24", "rate": 385000, "change": 1.2},
    {"name": "ذهب عيار 21", "rate": 337000, "change": 1.0},
    {"name": "ذهب عيار 18", "rate": 289000, "change": 0.9},
]

CARDS = [
    {"type": "Visa", "last4": "4242", "balance": 10, "status": "نشطة"},
    {"type": "Mastercard", "last4": "8813", "balance": 25, "status": "مجمدة"},
]

TRANSACTIONS = [
    {"title": "إيداع رصيد", "amount": "+100,000 YER", "date": "اليوم"},
    {"title": "شراء بطاقة Visa", "amount": "-17,000 YER", "date": "اليوم"},
    {"title": "شحن Free Fire", "amount": "-5,000 YER", "date": "أمس"},
    {"title": "تحويل إلى أحمد", "amount": "+50,000 YER", "date": "أمس"},
]

screen_index = 0
favorites_list = None
all_list = None
gold_list = None
search_field = None
body = None
wallet_api = WalletAPI()


def card_box(title, amount, icon, color):
    return ft.Container(
        expand=True,
        padding=16,
        border_radius=16,
        bgcolor="#121B2E",
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(icon, color=color, size=30),
                ft.Text(title, color="#F8FAFC", size=14),
                ft.Text(amount, color=color, weight=ft.FontWeight.BOLD),
            ],
        ),
    )

def home_screen():
    return ft.Column(
        spacing=16,
        controls=[
            ft.Container(
                padding=20,
                border_radius=20,
                bgcolor="#16213A",
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("الرصيد الكلي", color="#94A3B8"),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "1,250,000 YER",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                    color="#F8FAFC",
                                ),
                                ft.IconButton(
                                    ft.Icons.VISIBILITY,
                                    icon_color="#94A3B8",
                                ),
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Button(
                                    "إرسال",
                                    icon=ft.Icons.SEND,
                                    bgcolor="#2F7BFF",
                                    color="white",
                                    on_click=lambda e: show_message(
                                        e.page,
                                        "on_click=go_to(5),",
                                    ),
                                ),
                                ft.Button(
                                    "استلام",
                                    icon=ft.Icons.QR_CODE,
                                    bgcolor="#1B2740",
                                    color="white",
                                    on_click=lambda e: show_message(
                                        e.page,
                                        "امسح رمز QR لاستلام المال",
                                    ),
                                ),
                                ft.Button(
                                    "شحن",
                                    icon=ft.Icons.ADD_CARD,
                                    bgcolor="#1B2740",
                                    color="white",
                                    on_click=go_to(3),
                                ),
                            ]
                        ),
                    ],
                ),
            ),
            ft.Text(
                "أسعار اليوم",
                size=18,
                weight=ft.FontWeight.BOLD,
                color="#E5B84B",
            ),
            ft.Row(
                controls=[
                    card_box("USD", "1,650 YER", ft.Icons.PAYMENTS, "#22C55E"),
                    card_box("SAR", "440 YER", ft.Icons.PAYMENTS, "#22C55E"),
                ]
            ),
            ft.Row(
                controls=[
                    card_box("ذهب 24", "385,000 YER", ft.Icons.STAR, "#E5B84B"),
                    card_box("ذهب 21", "337,000 YER", ft.Icons.STAR, "#E5B84B"),
                ]
            ),
            ft.Text(
                "الخدمات",
                size=18,
                weight=ft.FontWeight.BOLD,
                color="#F8FAFC",
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        "البطاقات",
                        icon=ft.Icons.CREDIT_CARD,
                        bgcolor="#121B2E",
                        color="#2F7BFF",
                        on_click=go_to(2),
                    ),
                    ft.Button(
                        "ألعاب",
                        icon=ft.Icons.SPORTS_ESPORTS,
                        bgcolor="#121B2E",
                        color="#E5B84B",
                        on_click=go_to(3),
                    ),
                ]
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        "اشتراكات",
                        icon=ft.Icons.PLAY_CIRCLE,
                        bgcolor="#121B2E",
                        color="#EF4444",
                        on_click=go_to(3),
                    ),
                    ft.Button(
                        "فواتير",
                        icon=ft.Icons.RECEIPT,
                        bgcolor="#121B2E",
                        color="#22C55E",
                        on_click=go_to(3),
                    ),
                ]
            ),
        ],
    )


    return ft.Column(
        spacing=16,
        controls=[
            ft.Container(
                padding=20,
                border_radius=20,
                bgcolor="#16213A",
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("الرصيد الكلي", color="#94A3B8"),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "1,250,000 YER",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                    color="#F8FAFC",
                                ),
                                ft.IconButton(
                                    ft.Icons.VISIBILITY,
                                    icon_color="#94A3B8",
                                ),
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Button(
                                    "إرسال",
                                    icon=ft.Icons.SEND,
                                    bgcolor="#2F7BFF",
                                    color="white",
                                    on_click=go_to(5),
                                ),
                                ft.Button(
                                    "استلام",
                                    icon=ft.Icons.QR_CODE,
                                    bgcolor="#1B2740",
                                    color="white",
                                    on_click=lambda e: show_message(
                                        e.page, "امسح رمز QR لاستلام المال"
                                    ),
                                ),
                                ft.Button(
                                    "شحن",
                                    icon=ft.Icons.ADD_CARD,
                                    bgcolor="#1B2740",
                                    color="white",
                                    on_click=go_to(3),
                                ),
                            ]
                        ),
                    ],
                ),
            ),
            ft.Text(
                "أسعار اليوم",
                size=18,
                weight=ft.FontWeight.BOLD,
                color="#E5B84B",
            ),
            ft.Row(
                controls=[
                    card_box("USD", "1,650 YER", ft.Icons.PAYMENTS, "#22C55E"),
                    card_box("SAR", "440 YER", ft.Icons.PAYMENTS, "#22C55E"),
                ]
            ),
            ft.Row(
                controls=[
                    card_box("ذهب 24", "385,000 YER", ft.Icons.STAR, "#E5B84B"),
                    card_box("ذهب 21", "337,000 YER", ft.Icons.STAR, "#E5B84B"),
                ]
            ),
            ft.Text(
                "الخدمات",
                size=18,
                weight=ft.FontWeight.BOLD,
                color="#F8FAFC",
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        "البطاقات",
                        icon=ft.Icons.CREDIT_CARD,
                        bgcolor="#121B2E",
                        color="#2F7BFF",
                        on_click=go_to(2),
                    ),
                    ft.Button(
                        "ألعاب",
                        icon=ft.Icons.SPORTS_ESPORTS,
                        bgcolor="#121B2E",
                        color="#E5B84B",
                        on_click=go_to(3),
                    ),
                ]
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        "اشتراكات",
                        icon=ft.Icons.PLAY_CIRCLE,
                        bgcolor="#121B2E",
                        color="#EF4444",
                        on_click=go_to(3),
                    ),
                    ft.Button(
                        "فواتير",
                        icon=ft.Icons.RECEIPT,
                        bgcolor="#121B2E",
                        color="#22C55E",
                        on_click=go_to(3),
                    ),
                ]
            ),
        ],
    )

    return ft.Column(
        spacing=16,
        controls=[
            ft.Container(
                padding=20,
                border_radius=20,
                bgcolor="#16213A",
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("الرصيد الكلي", color="#94A3B8"),
                        ft.Row(
                            controls=[
                                ft.Text("1,250,000 YER", size=30, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                                ft.IconButton(ft.Icons.VISIBILITY, icon_color="#94A3B8"),
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Button("إرسال", icon=ft.Icons.SEND, bgcolor="#2F7BFF", color="white"),
                                ft.Button("استلام", icon=ft.Icons.QR_CODE, bgcolor="#1B2740", color="white"),
                                ft.Button("شحن", icon=ft.Icons.ADD_CARD, bgcolor="#1B2740", color="white"),
                            ]
                        ),
                    ],
                ),
            ),
            ft.Text("أسعار اليوم", size=18, weight=ft.FontWeight.BOLD, color="#E5B84B"),
            ft.Row(
                controls=[
                    card_box("USD", "1,650 YER", ft.Icons.PAYMENTS, "#22C55E"),
                    card_box("SAR", "440 YER", ft.Icons.PAYMENTS, "#22C55E"),
                ]
            ),
            ft.Row(
                controls=[
                    card_box("ذهب 24", "385,000 YER", ft.Icons.STAR, "#E5B84B"),
                    card_box("ذهب 21", "337,000 YER", ft.Icons.STAR, "#E5B84B"),
                ]
            ),
            ft.Text("الخدمات", size=18, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
            ft.Row(
                controls=[
                    card_box("بطاقات", "Visa / MC", ft.Icons.CREDIT_CARD, "#2F7BFF"),
                    card_box("ألعاب", "شحن", ft.Icons.SPORTS_ESPORTS, "#E5B84B"),
                ]
            ),
            ft.Row(
                controls=[
                    card_box("اشتراكات", "Netflix وغيرها", ft.Icons.PLAY_CIRCLE, "#EF4444"),
                    card_box("فواتير", "دفع", ft.Icons.RECEIPT, "#22C55E"),
                ]
            ),
        ],
    )


def currency_row(c):
    if c["change"] >= 0:
        change_color = ft.Colors.GREEN_400
        change_text = "▲ " + str(c["change"]) + "%"
    else:
        change_color = ft.Colors.RED_400
        change_text = "▼ " + str(abs(c["change"])) + "%"

    star_color = ft.Colors.AMBER_400 if c["fav"] else "#475569"

    return ft.Container(
        padding=12,
        border_radius=14,
        bgcolor="#121B2E",
        border=ft.Border.all(1, "#2B3A55"),
        content=ft.Row(
            controls=[
                ft.Text(c["flag"], size=26),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(c["code"] + " — " + c["name"], color="#F8FAFC", weight=ft.FontWeight.BOLD),
                        ft.Text(format(c["rate"], ",") + " YER", color="#94A3B8", size=13),
                    ],
                ),
                ft.Text(change_text, color=change_color, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.Icons.STAR,
                    icon_color=star_color,
                    on_click=lambda e, c=c: toggle_favorite(e, c),
                ),
            ]
        ),
    )


def gold_row(g):
    if g["change"] >= 0:
        change_color = ft.Colors.GREEN_400
        change_text = "▲ " + str(g["change"]) + "%"
    else:
        change_color = ft.Colors.RED_400
        change_text = "▼ " + str(abs(g["change"])) + "%"

    return ft.Container(
        padding=12,
        border_radius=14,
        bgcolor="#1B2740",
        border=ft.Border.all(1, "#E5B84B"),
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.STAR, color="#E5B84B"),
                ft.Column(
                    expand=True,
                    controls=[
                        ft.Text(g["name"], color="#F8FAFC", weight=ft.FontWeight.BOLD),
                        ft.Text(format(g["rate"], ",") + " YER / جرام", color="#E5B84B"),
                    ],
                ),
                ft.Text(change_text, color=change_color),
            ]
        ),
    )


def build_currency_list(query=""):
    q = query.strip().lower()
    rows = []
    for c in CURRENCIES:
        if q == "" or q in c["code"].lower() or q in c["name"].lower():
            rows.append(currency_row(c))
    return rows


def toggle_favorite(e, currency):
    currency["fav"] = not currency["fav"]
    refresh_lists()
    e.page.update()


def refresh_lists():
    favorites_list.controls = build_currency_list()
    all_list.controls = build_currency_list(search_field.value)
    gold_list.controls = [gold_row(g) for g in GOLD]


def search_changed(e):
    all_list.controls = build_currency_list(search_field.value)
    e.page.update()


def currencies_screen():
    global favorites_list, all_list, gold_list, search_field

    search_field = ft.TextField(
        hint_text="ابحث: USD، دولار، ريال...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=12,
        bgcolor="#121B2E",
        border_color="#2B3A55",
        on_change=search_changed,
    )

    favorites_list = ft.Column(spacing=10)
    all_list = ft.Column(spacing=10)
    gold_list = ft.Column(spacing=10)

    refresh_lists()

    return ft.Column(
        spacing=16,
        controls=[
            ft.Text("العملات", size=22, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
            search_field,
            ft.Text("المفضلة", size=18, weight=ft.FontWeight.BOLD, color="#E5B84B"),
            favorites_list,
            ft.Text("أسعار الذهب", size=18, weight=ft.FontWeight.BOLD, color="#E5B84B"),
            gold_list,
            ft.Text("كل العملات", size=18, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
            all_list,
        ],
    )


def cards_screen():
    cards = []
    for c in CARDS:
        cards.append(
            ft.Container(
                padding=16,
                border_radius=16,
                bgcolor="#16213A",
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(c["type"] + " •••• " + c["last4"], color="#F8FAFC", weight=ft.FontWeight.BOLD),
                        ft.Text("الرصيد: " + str(c["balance"]) + "$", color="#22C55E"),
                        ft.Text("الحالة: " + c["status"], color="#94A3B8"),
                        ft.Row(
                            controls=[
                                ft.Button("شحن", bgcolor="#2F7BFF", color="white"),
                                ft.Button("تجميد", bgcolor="#1B2740", color="white"),
                            ]
                        ),
                    ],
                ),
            )
        )

    return ft.Column(
        spacing=16,
        controls=[
            ft.Text("البطاقات الافتراضية", size=22, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
            ft.Button(
                "إنشاء بطاقة جديدة",
                icon=ft.Icons.ADD,
                bgcolor="#E5B84B",
                color="black",
                width=100000,
            ),
        ] + cards,
    )


def services_screen():
    return ft.Column(
        spacing=16,
        controls=[
            ft.Text("الخدمات", size=22, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
            ft.Row(controls=[card_box("Free Fire", "شحن جواهر", ft.Icons.SPORTS_ESPORTS, "#E5B84B"),
                             card_box("PUBG", "شحن UC", ft.Icons.GAMEPAD, "#2F7BFF")]),
            ft.Row(controls=[card_box("Google Play", "بطاقة هدايا", ft.Icons.SHOP, "#22C55E"),
                             card_box("Netflix", "اشتراك", ft.Icons.PLAY_CIRCLE, "#EF4444")]),
            ft.Row(controls=[card_box("رصيد هاتف", "شحن", ft.Icons.PHONE, "#2F7BFF"),
                             card_box("إنترنت", "باقات", ft.Icons.WIFI, "#22C55E")]),
        ],
    )


def history_screen():
    rows = []
    for t in TRANSACTIONS:
        color = ft.Colors.GREEN_400 if t["amount"].startswith("+") else ft.Colors.RED_400
        rows.append(
            ft.Container(
                padding=12,
                border_radius=14,
                bgcolor="#121B2E",
                content=ft.Row(
                    controls=[
                        ft.Column(
                            expand=True,
                            controls=[
                                ft.Text(t["title"], color="#F8FAFC", weight=ft.FontWeight.BOLD),
                                ft.Text(t["date"], color="#94A3B8", size=12),
                            ],
                        ),
                        ft.Text(t["amount"], color=color, weight=ft.FontWeight.BOLD),
                    ]
                ),
            )
        )

    return ft.Column(
        spacing=16,
        controls=[ft.Text("سجل العمليات", size=22, weight=ft.FontWeight.BOLD, color="#F8FAFC")] + rows,
    )


def change_screen(e):
    global screen_index
    screen_index = e.control.selected_index
    update_body(e.page)


def transfer_screen():
    recipient_field = ft.TextField(
        label="رقم هاتف المستفيد",
        hint_text="+967XXXXXXXXX",
        keyboard_type=ft.KeyboardType.PHONE,
    )

    amount_field = ft.TextField(
        label="المبلغ",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    currency_dd = ft.Dropdown(
        label="العملة",
        value="YER",
        options=[
            ft.DropdownOption(key="YER", content=ft.Text("YER - ريال يمني")),
            ft.DropdownOption(key="SAR", content=ft.Text("SAR - ريال سعودي")),
            ft.DropdownOption(key="AED", content=ft.Text("AED - درهم إماراتي")),
            ft.DropdownOption(key="USD", content=ft.Text("USD - دولار أمريكي")),
        ],
    )

    description_field = ft.TextField(
        label="وصف التحويل",
        value="تحويل داخلي",
        multiline=True,
        max_length=200,
    )

    status_text = ft.Text(
        "تحويل داخلي بين حسابات SULTAN WALLET",
        color="#D4AF37",
        size=14,
    )

    submit_button = ft.Button(
        "تأكيد التحويل الداخلي",
        icon=ft.Icons.CHECK_CIRCLE,
        bgcolor="#22C55E",
        color="black",
    )

    def confirm_transfer(e):
        phone = (recipient_field.value or "").strip()
        amount = (amount_field.value or "").strip()
        currency = currency_dd.value
        description = (description_field.value or "تحويل داخلي").strip()

        if not phone or not amount:
            show_message(e.page, "أدخل رقم المستفيد والمبلغ أولاً")
            return

        try:
            if float(amount) <= 0:
                raise ValueError()
        except ValueError:
            show_message(e.page, "المبلغ غير صحيح")
            return

        if not wallet_api.token:
            show_message(
                e.page,
                "يلزم تسجيل الدخول أولاً لفتح جلسة آمنة قبل التحويل."
            )
            return

        submit_button.disabled = True
        status_text.value = "جارٍ إرسال طلب التحويل والتحقق منه..."
        e.page.update()

        payload = {
            "recipient_phone": phone,
            "amount": amount,
            "currency": currency,
            "idempotency_key": secrets.token_hex(16),
            "description": description,
        }

        try:
            result = wallet_api.transfer(payload)
            reference = result.get("reference", "غير متوفر")
            status = result.get("status", "unknown")

            status_text.value = (
                f"حالة العملية: {status} | الرقم المرجعي: {reference}"
            )
            show_message(
                e.page,
                f"استلم الخادم نتيجة التحويل. الرقم المرجعي: {reference}"
            )
        except Exception as ex:
            status_text.value = "لم يتم تأكيد التحويل"
            show_message(e.page, f"تعذر تنفيذ التحويل: {ex}")
        finally:
            submit_button.disabled = False
            e.page.update()

    submit_button.on_click = confirm_transfer

    return ft.Column(
        spacing=16,
        controls=[
            ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        icon_color="#F8FAFC",
                        on_click=go_to(0),
                    ),
                    ft.Text(
                        "التحويل الداخلي",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#F8FAFC",
                    ),
                ]
            ),
            ft.Text(
                "إرسال الرصيد إلى مستخدم آخر داخل المحفظة",
                color="#94A3B8",
            ),
            recipient_field,
            amount_field,
            currency_dd,
            description_field,
            status_text,
            submit_button,
        ],
    )

def update_body(page):
    if screen_index == 0:
        body.content = home_screen()
    elif screen_index == 1:
        body.content = currencies_screen()
    elif screen_index == 2:
        body.content = cards_screen()
    elif screen_index == 3:
        body.content = services_screen()
    elif screen_index == 4:
        body.content = history_screen()
    elif screen_index == 5:
        body.content = transfer_screen()
    page.update()


def main(page):
    global body

    page.title = "SULTAN_WALLET"
    page.bgcolor = "#0B1220"
    page.padding = 16
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK

    page.appbar = ft.AppBar(
        title=ft.Text("SULTAN_WALLET", weight=ft.FontWeight.BOLD, color="#E5B84B"),
        bgcolor="#0B1220",
        actions=[ft.IconButton(ft.Icons.NOTIFICATIONS, icon_color="#F8FAFC")],
    )

    body = ft.Container(expand=True)

    page.navigation_bar = ft.NavigationBar(
        bgcolor="#121B2E",
        selected_index=0,
        on_change=change_screen,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="الرئيسية"),
            ft.NavigationBarDestination(icon=ft.Icons.CURRENCY_EXCHANGE_OUTLINED, selected_icon=ft.Icons.CURRENCY_EXCHANGE, label="العملات"),
            ft.NavigationBarDestination(icon=ft.Icons.CREDIT_CARD_OUTLINED, selected_icon=ft.Icons.CREDIT_CARD, label="البطاقات"),
            ft.NavigationBarDestination(icon=ft.Icons.APPS_OUTLINED, selected_icon=ft.Icons.APPS, label="الخدمات"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="السجل"),
        ],
    )

    body.content = home_screen()

    page.add(body)

def show_message(page, text):
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(text),
            bgcolor="#1B2740",
        )
    )


def go_to(screen_number):
    global screen_index
    screen_index = screen_number
    return lambda e: update_body(e.page)
if __name__ == "__main__":
    ft.run(main)

# Trigger Android APK build from commercial-build; no runtime behavior change.
