import flet as ft

def main(page: ft.Page):
    page.title = "Sultan Wallet"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#0D0D11"
    
    # ------------------ 1. نظام الحماية بالبصمة / PIN ------------------
    def check_pin(e):
        if pin_input.value == "1234":
            page.navigation_bar.visible = True
            show_dashboard()
        else:
            pin_input.error_text = "رمز PIN غير صحيح"
            page.update()

    pin_input = ft.TextField(
        label="أدخل رمز PIN السري",
        password=True,
        can_reveal_password=True,
        text_align=ft.TextAlign.CENTER,
        width=260,
        border_color="#FFD700",
        focused_border_color="#D4AF37",
        border_radius=15,
        color="#FFFFFF"
    )

    lock_screen = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.icons.LOCK_ROUNDED, size=80, color="#FFD700"),
                ft.Text("SULTAN WALLET", size=24, weight=ft.FontWeight.BOLD, color="#FFD700"),
                ft.Text("محفظة سلطان زمانه - حماية فائقة", size=14, color="#AAAAAA"),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                pin_input,
                ft.ElevatedButton(
                    content=ft.Row([ft.Icon(ft.icons.FINGERPRINT), ft.Text("فتح بالبصمة / الدخول")]),
                    style=ft.ButtonStyle(
                        color="#0D0D11",
                        bgcolor="#FFD700",
                        shape=ft.RoundedRectangleBorder(radius=15)
                    ),
                    on_click=check_pin,
                    width=260,
                    height=50
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    # ------------------ 2. لوحة التحكم والإحصائيات والواجهة الملكية ------------------
    def get_dashboard():
        return ft.ListView(
            padding=ft.padding.all(20),
            controls=[
                # الهيدر الترحيبي
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("أهلاً بك يا سلطان! 🦅", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            ft.Text("Sultan Wallet - الحساب الملكي", size=12, color="#FFD700")
                        ]),
                        ft.CircleAvatar(
                            content=ft.Icon(ft.icons.PERSON, color="#0D0D11"),
                            bgcolor="#FFD700",
                            radius=22
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(height=25, color=ft.colors.TRANSPARENT),

                # بطاقة الرصيد الفخمة
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("الرصيد الكلي المتاح", color="#DDDDDD", size=14),
                            ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, color="#FFD700")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text("$128,450.00", size=32, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        ft.Divider(height=10, color="#333333"),
                        ft.Row([
                            ft.Row([ft.Icon(ft.icons.ARROW_UPWARD, color="#00FF7F", size=16), ft.Text("الدخل: $45,000", color="#00FF7F", size=12)]),
                            ft.Row([ft.Icon(ft.icons.ARROW_DOWNWARD, color="#FF4500", size=16), ft.Text("المصروف: $12,300", color="#FF4500", size=12)])
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]),
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=["#1E1E26", "#2D2D3A", "#141419"]
                    ),
                    padding=20,
                    border_radius=20,
                    border=ft.border.all(1, "#FFD700")
                ),
                ft.Divider(height=25, color=ft.colors.TRANSPARENT),

                # 3. قسم الإحصائيات والرسوم البيانية التفاعلية
                ft.Text("إحصائيات المصروفات والنمو 📊", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("استهلاك الميزانية الشهرية", color="#AAAAAA"), ft.Text("65%", color="#FFD700")]),
                        ft.ProgressBar(value=0.65, color="#FFD700", bgcolor="#333333", height=10),
                        ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                        ft.Row([
                            ft.Column([ft.Text("الأرباح", size=12, color="#888888"), ft.Text("+18.5%", color="#00FF7F", weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("الاستثمار", size=12, color="#888888"), ft.Text("$34,000", color="#FFD700", weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("الأمان", size=12, color="#888888"), ft.Text("100%", color="#00E5FF", weight=ft.FontWeight.BOLD)])
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
                    ]),
                    padding=15,
                    bgcolor="#181820",
                    border_radius=15
                ),
                ft.Divider(height=25, color=ft.colors.TRANSPARENT),

                # أزرار العمليات السريعة
                ft.Text("الخدمات السريعة ⚡", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Row([
                    ft.ElevatedButton("إرسال أموال 💸", style=ft.ButtonStyle(bgcolor="#FFD700", color="#000000")),
                    ft.ElevatedButton("تعبئة رصيد 💳", style=ft.ButtonStyle(bgcolor="#2D2D3A", color="#FFFFFF")),
                    ft.ElevatedButton("تقرير PDF 📄", style=ft.ButtonStyle(bgcolor="#2D2D3A", color="#FFD700"))
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
            ft.NavigationDestination(icon=ft.icons.HOME, label="الرئيسية"),
            ft.NavigationDestination(icon=ft.icons.BAR_CHART, label="الإحصائيات"),
            ft.NavigationDestination(icon=ft.icons.SECURITY, label="الأمان"),
            ft.NavigationDestination(icon=ft.icons.SETTINGS, label="الإعدادات"),
        ]
    )

    page.add(lock_screen)

ft.app(target=main)
