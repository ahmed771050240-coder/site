import flet as ft

GOLD = "#D4AF37"
TEAL = "#14B8A6"
DARK = "#070A10"
CARD = "#0F141E"

class WalletSultan:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "WALLET SULTAN"
        self.page.bgcolor = DARK
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.rtl = True
        self.tab = 0
        self.filter = "الكل"

    def build(self):
        self.page.views.clear()
        if self.tab == 0:
            self.page.views.append(self.home())
        elif self.tab == 1:
            self.page.views.append(self.cards())
        elif self.tab == 2:
            self.page.views.append(self.stats())
        else:
            self.page.views.append(self.settings())
        self.page.update()

    def home(self):
        header = ft.Container(
            padding=ft.padding.only(top=44, left=14, right=14, bottom=10),
            content=ft.Column([
                ft.Row([
                    ft.Container(width=32, height=32, border_radius=16, bgcolor="#121821", border=ft.border.all(1,"rgba(255,255,255,0.08)"), content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE, size=16, color="#888")),
                    ft.Text("WALLET SULTAN", size=14, weight=ft.FontWeight.BOLD, color="white", expand=True, text_align=ft.TextAlign.CENTER),
                    ft.Container(width=32, height=32, border_radius=16, bgcolor="#121821", content=ft.Icon(ft.Icons.DIAMOND, size=14, color=GOLD)),
                ]),
                ft.Container(height=10),
                ft.Row([
                    ft.Container(padding=ft.padding.symmetric(6,12), border_radius=20, bgcolor="#131A26", border=ft.border.all(1,"rgba(255,255,255,0.06)"), content=ft.Row([ft.Container(width=6, height=6, border_radius=3, bgcolor="#22C55E"), ft.Text("PRIVATE WALLET SULTAN", size=8, color="#7A8AA0")], spacing=6)),
                    ft.Container(expand=True),
                    ft.Container(width=36, height=36, border_radius=18, bgcolor="#1A2416", border=ft.border.all(1,"rgba(34,197,94,0.2)"), alignment=ft.alignment.center, content=ft.Text("انس", size=10, color="#22C55E", weight=ft.FontWeight.BOLD))
                ]),
                ft.Container(height=8),
                ft.Row([ft.Icon(ft.Icons.STARS, size=14, color=GOLD), ft.Text("أهلاً، أبو سلطان", size=18, weight=ft.FontWeight.BOLD, color="white")], spacing=6),
                ft.Text("يومك جميل اليوم • +14 يوم متتالي", size=11, color="#5A6A80"),
            ])
        )

        balance = ft.Container(
            border_radius=22,
            gradient=ft.LinearGradient(["#101A26","#0C121C"]),
            border=ft.border.all(1,"rgba(255,255,255,0.06)"),
            padding=16,
            content=ft.Column([
                ft.Row([ft.Text("الرصيد الكلي", size=11, color="#6A7A90"), ft.Container(expand=True), ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color="#5A6A80"), ft.Text("WALLET SULTAN", size=8, color="#444")]),
                ft.Container(height=8),
                ft.Row([ft.Text("50, 47,892 ر.س", size=32, weight=ft.FontWeight.BOLD, color="white")], alignment=ft.MainAxisAlignment.END),
                ft.Row([ft.Text("مقارنة - محفظة WALLET SULTAN", size=9, color="#4A5A70"), ft.Container(padding=ft.padding.symmetric(3,6), border_radius=8, bgcolor="rgba(34,197,94,0.12)", content=ft.Text("2.4% ↑", size=8, color="#22C55E"))]),
                ft.Container(height=12),
                ft.Row([
                    ft.Container(expand=True, height=56, border_radius=14, bgcolor="#0E141E", border=ft.border.all(1,"rgba(255,255,255,0.04)"), padding=10, content=ft.Row([ft.Container(width=32, height=32, border_radius=16, bgcolor="rgba(212,175,55,0.12)", content=ft.Icon(ft.Icons.ARROW_OUTWARD, size=14, color=GOLD)), ft.Column([ft.Text("إجمالي المصروفات - باي", size=8, color="#5A6A80"), ft.Text("1,335.50 ر.س", size=12, weight=ft.FontWeight.BOLD, color="white")], spacing=2)])),
                    ft.Container(width=8),
                    ft.Container(expand=True, height=56, border_radius=14, bgcolor="#0E141E", border=ft.border.all(1,"rgba(255,255,255,0.04)"), padding=10, content=ft.Row([ft.Container(width=32, height=32, border_radius=16, bgcolor="rgba(34,197,94,0.12)", content=ft.Icon(ft.Icons.CALL_RECEIVED, size=14, color="#22C55E")), ft.Column([ft.Text("دخل الشهر الحالي", size=8, color="#5A6A80"), ft.Text("24,300+ ر.س", size=12, weight=ft.FontWeight.BOLD, color="white")], spacing=2)])),
                ])
            ])
        )

        quick = ft.Column([
            ft.Row([ft.Text("إجراءات سريعة", size=13, weight=ft.FontWeight.BOLD, color="white"), ft.Container(expand=True), ft.Text("لتخصيص", size=10, color="#5A6A80")]),
            ft.Container(height=8),
            ft.Row([
                self.q_btn("تحويل", ft.Icons.SEND, "#1A3A2E"),
                self.q_btn("شحن", ft.Icons.BOLT, "#2A2410"),
                self.q_btn("سحب", ft.Icons.ARROW_DOWNWARD, "#1E2A3A"),
                self.q_btn("كشف حساب", ft.Icons.RECEIPT_LONG, "#2A1E3A"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ])

        my_card = ft.Container(
            border_radius=20,
            gradient=ft.LinearGradient(["#1A1F2A","#0F141E"]),
            border=ft.border.all(1,"rgba(255,255,255,0.08)"),
            padding=14,
            content=ft.Column([
                ft.Row([ft.Text("بطاقاتي", size=12, weight=ft.FontWeight.BOLD, color="white"), ft.Container(expand=True), ft.Text("عرض الكل ›", size=10, color="#5A6A80")]),
                ft.Container(height=8),
                ft.Container(
                    height=110, border_radius=14,
                    gradient=ft.LinearGradient(["#1E293B","#0F172A"]),
                    border=ft.border.all(1,"rgba(212,175,55,0.15)"),
                    padding=12,
                    content=ft.Column([
                        ft.Row([ft.Text("WALLET SULTAN", size=8, color="#6A7A90"), ft.Container(expand=True), ft.Container(width=32, height=20, border_radius=4, bgcolor=GOLD, content=ft.Icon(ft.Icons.CREDIT_CARD, size=12, color="black"))]),
                        ft.Text("SULTAN WALLET PRIVATE EDITION", size=7, color="#4A5A70"),
                        ft.Container(height=8),
                        ft.Text("4582 •••• •••• ••••", size=16, color="white", font_family="monospace"),
                        ft.Row([
                            ft.Column([ft.Text("EXPIRES", size=6, color="#555"), ft.Text("08/28", size=10, color="white")], spacing=1),
                            ft.Container(expand=True),
                            ft.Column([ft.Text("HOLDER", size=6, color="#555"), ft.Text("ABU SULTAN", size=10, color="white")], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.END),
                            ft.Container(width=36, height=20, border_radius=4, bgcolor="#E5E5E5", alignment=ft.alignment.center, content=ft.Text("mada", size=8, weight=ft.FontWeight.BOLD, color="black"))
                        ])
                    ])
                )
            ])
        )

        ops = ft.Column([
            ft.Row([ft.Text("العمليات الأخيرة", size=13, weight=ft.FontWeight.BOLD, color="white"), ft.Container(expand=True), ft.Row([self.chip("الكل", True), self.chip("صادر", False), self.chip("وارد", False)], spacing=6)]),
            ft.Container(height=8),
            self.op_item("متجر نون", "تسوق - إلكترونيات", "- 249.00 ر.س", ft.Icons.SHOPPING_BAG),
            self.op_item("راتب شهري", "STC Pay - تحويل من الراجحي", "+ 12,450.00 ر.س", ft.Icons.ACCOUNT_BALANCE_WALLET, True),
            self.op_item("محطة الدريس", "وقود - محطة الدريس", "- 180.50 ر.س", ft.Icons.LOCAL_GAS_STATION),
            self.op_item("مطعم البيك", "Apple Pay - 12:40 م", "- 88.00 ر.س", ft.Icons.RESTAURANT),
            self.op_item("أحمد الغامدي", "تحويل - 13 ر.س", "- 500.00 ر.س", ft.Icons.SEND),
            self.op_item("قسط تمارا", "تقسيط - تمارا", "- 320.00 ر.س", ft.Icons.CREDIT_CARD),
            ft.Container(height=8),
            ft.Text("عرض كل العمليات ›", size=11, color="#5A6A80", text_align=ft.TextAlign.CENTER),
            ft.Container(height=100)
        ])

        content = ft.Column([header, ft.Container(padding=ft.padding.symmetric(12,0), content=ft.Column([balance, ft.Container(height=16), quick, ft.Container(height=16), my_card, ft.Container(height=16), ops], scroll=ft.ScrollMode.AUTO, expand=True))], expand=True)
        return ft.View(route="/", bgcolor=DARK, padding=0, navigation_bar=self.bottom_nav(0), controls=[content])

    def cards(self):
        return ft.View(route="/cards", bgcolor=DARK, padding=12, navigation_bar=self.bottom_nav(1), controls=[ft.Column([
            ft.Text("محفظتي • البطاقات", size=18, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=12),
            self.big_card("4582 •••• •••• ••••", "ABU SULTAN • 08/28", "أساسية", "#1E293B", False, "الكارت الأساسي"),
            self.big_card("9021 •••• •••• ••••", "ABU SULTAN • 11/27", "افتراضية", GOLD, True, "الذهبية المميزة"),
            self.big_card("1134 •••• •••• ••••", "ABU SULTAN • 03/29", "افتراضية", TEAL, False, "رقم خاص"),
            ft.Container(height=60, border_radius=16, border=ft.border.all(1, ft.BorderStyle.DASHED, "rgba(255,255,255,0.15)"), bgcolor="rgba(255,255,255,0.02)", alignment=ft.alignment.center, content=ft.Row([ft.Icon(ft.Icons.ADD, size=18, color="#666"), ft.Text("إضافة بطاقة جديدة", size=12, color="#666")], alignment=ft.MainAxisAlignment.CENTER)),
            ft.Container(height=16),
            ft.Container(border_radius=16, bgcolor=CARD, padding=16, content=ft.Column([
                ft.Text("حدود البطاقات", size=12, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=8),
                ft.Row([ft.Text("الإنفاق الشهري", size=10, color="#666"), ft.Text("3,240 / 5,000 ر.س", size=10, color="white")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=4, bgcolor="#1A2332", border_radius=4, content=ft.Container(width=180, height=4, bgcolor=TEAL, border_radius=4)),
                ft.Container(height=8),
                ft.Row([ft.Text("السحب اليومي", size=10, color="#666"), ft.Text("800 / 2,000 ر.س", size=10, color="white")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=4, bgcolor="#1A2332", border_radius=4, content=ft.Container(width=100, height=4, bgcolor=GOLD, border_radius=4)),
            ])),
            ft.Container(height=80)
        ], scroll=ft.ScrollMode.AUTO, expand=True)])

    def stats(self):
        return ft.View(route="/stats", bgcolor=DARK, padding=16, navigation_bar=self.bottom_nav(2), controls=[ft.Column([
            ft.Text("الإحصائيات", size=18, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=16),
            ft.Container(border_radius=16, bgcolor=CARD, padding=16, content=ft.Column([ft.Text("إجمالي المصروفات - باي", size=11, color="#6A7A90"), ft.Text("1,335.50 ر.س", size=28, weight=ft.FontWeight.BOLD, color="white"), ft.Container(padding=ft.padding.symmetric(4,8), border_radius=8, bgcolor="rgba(239,68,68,0.12)", content=ft.Text("- 13% عن ديسمبر", size=9, color="#EF4444"))])),
            ft.Container(height=12),
            ft.Row([ft.Container(expand=True, border_radius=14, bgcolor=CARD, padding=12, content=ft.Column([ft.Text("أكثر فئة إنفاق", size=9, color="#5A6A80"), ft.Text("تسوق • 42%", size=12, weight=ft.FontWeight.BOLD, color="white"), ft.Container(height=4, bgcolor="#1A2332", border_radius=4, content=ft.Container(width=60, bgcolor="#8B5CF6", height=4, border_radius=4))])), ft.Container(width=8), ft.Container(expand=True, border_radius=14, bgcolor=CARD, padding=12, content=ft.Column([ft.Text("توفر هذا الشهر", size=9, color="#5A6A80"), ft.Text("1,850+ ر.س", size=12, weight=ft.FontWeight.BOLD, color="#22C55E"), ft.Text("من أصل 3,000 ر.س", size=8, color="#444")]))]),
            ft.Container(height=80)
        ], scroll=ft.ScrollMode.AUTO, expand=True)])

    def settings(self):
        return ft.View(route="/settings", bgcolor=DARK, padding=16, navigation_bar=self.bottom_nav(3), controls=[ft.Column([
            ft.Text("الإعدادات", size=18, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=16),
            ft.Container(border_radius=16, bgcolor=CARD, content=ft.Column([self.set_row("الأمان والخصوصية", "بصمة - Face ID - كلمة مرور", ft.Icons.FINGERPRINT), ft.Divider(height=1, color="rgba(255,255,255,0.04)"), self.set_row("الإشعارات", "إدارة التنبيهات والرسائل", ft.Icons.NOTIFICATIONS), ft.Divider(height=1, color="rgba(255,255,255,0.04)"), self.set_row("إدارة البطاقات", "تجميد - حدود - إعدادات", ft.Icons.CREDIT_CARD), ft.Divider(height=1, color="rgba(255,255,255,0.04)"), self.set_row("التطبيق", "اللغة - المظهر - المساحة", ft.Icons.PALETTE)])),
            ft.Container(height=12),
            ft.Container(border_radius=16, bgcolor="#131A1E", border=ft.border.all(1,"rgba(212,175,55,0.12)"), padding=14, content=ft.Row([ft.Container(width=36, height=36, border_radius=10, bgcolor="rgba(212,175,55,0.15)", content=ft.Icon(ft.Icons.STARS, size=18, color=GOLD)), ft.Column([ft.Text("SULTAN WALLET - الترقية إلى بلس", size=12, weight=ft.FontWeight.BOLD, color="white"), ft.Text("افتح جميع الميزات مع WALLET SULTAN PLUS - تحكم كامل، تقارير شهرية، دعم فني على مدار الساعة", size=9, color="#6A7A90")], expand=True)])),
            ft.Container(height=16),
            ft.Text("SULTAN WALLET الإصدار 3.4.1 - جميع الحقوق محفوظة", size=8, color="#333", text_align=ft.TextAlign.CENTER),
            ft.Container(height=80)
        ], scroll=ft.ScrollMode.AUTO, expand=True)])

    def q_btn(self, name, icon, bg):
        return ft.Column([ft.Container(width=56, height=56, border_radius=18, bgcolor=bg, border=ft.border.all(1,"rgba(255,255,255,0.06)"), alignment=ft.alignment.center, content=ft.Icon(icon, size=20, color="white")), ft.Container(height=6), ft.Text(name, size=11, color="#C0C8D4")], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
    def chip(self, t, s):
        return ft.Container(padding=ft.padding.symmetric(6,12), border_radius=20, bgcolor=GOLD if s else "#121821", border=ft.border.all(1, GOLD if s else "rgba(255,255,255,0.06)"), content=ft.Text(t, size=10, color="black" if s else "#6A7A90"))
    def op_item(self, name, sub, amt, icon, is_in=False):
        return ft.Container(border_radius=14, bgcolor=CARD, border=ft.border.all(1,"rgba(255,255,255,0.04)"), padding=12, content=ft.Row([ft.Container(width=40, height=40, border_radius=12, bgcolor="#121821", alignment=ft.alignment.center, content=ft.Icon(icon, size=18, color="#6A7A90")), ft.Column([ft.Text(name, size=12, weight=ft.FontWeight.BOLD, color="white"), ft.Text(sub, size=9, color="#5A6A80")], expand=True, spacing=2), ft.Text(amt, size=12, weight=ft.FontWeight.BOLD, color="#22C55E" if is_in else "white")]))
    def big_card(self, no, holder, badge, bg, is_gold, desc):
        return ft.Container(height=140, border_radius=20, bgcolor=bg if not is_gold else None, gradient=ft.LinearGradient([bg, "#8A6E24"]) if is_gold else ft.LinearGradient(["#1E293B","#0F172A"]), padding=16, content=ft.Column([ft.Row([ft.Text("WALLET SULTAN", size=8, color="rgba(255,255,255,0.5)"), ft.Container(expand=True), ft.Container(padding=ft.padding.symmetric(4,8), border_radius=6, bgcolor="rgba(0,0,0,0.3)", content=ft.Text(badge, size=8, color="white"))]), ft.Container(expand=True), ft.Text(desc, size=9, color="rgba(255,255,255,0.4)"), ft.Text(no, size=16, color="black" if is_gold else "white", font_family="monospace"), ft.Text(holder, size=10, color="rgba(0,0,0,0.6)" if is_gold else "rgba(255,255,255,0.6)")]))
    def set_row(self, title, sub, icon):
        return ft.Container(padding=12, content=ft.Row([ft.Container(width=36, height=36, border_radius=10, bgcolor="#121821", content=ft.Icon(icon, size=16, color="#6A7A90")), ft.Column([ft.Text(title, size=12, color="white"), ft.Text(sub, size=9, color="#5A6A80")], expand=True, spacing=2), ft.Icon(ft.Icons.CHEVRON_LEFT, size=16, color="#333")]))
    def bottom_nav(self, idx):
        return ft.NavigationBar(selected_index=idx, bgcolor="#0A0F1A", indicator_color="rgba(212,175,55,0.18)", height=68, on_change=self.nav_change, destinations=[ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="الرئيسية"), ft.NavigationBarDestination(icon=ft.Icons.CREDIT_CARD_OUTLINED, selected_icon=ft.Icons.CREDIT_CARD, label="البطاقات"), ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART_OUTLINED, selected_icon=ft.Icons.BAR_CHART, label="الإحصائيات"), ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="الإعدادات")])
    def nav_change(self, e):
        self.tab = e.control.selected_index
        self.page.go(["/","/cards","/stats","/settings"][self.tab])

def main(page: ft.Page):
    app = WalletSultan(page)
    page.on_route_change = lambda _: app.build()
    page.go("/")

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, host="0.0.0.0", assets_dir="assets")
