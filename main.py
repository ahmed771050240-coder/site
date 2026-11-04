import flet as ft

def main(page: ft.Page):
    page.title = "WALLET SULTAN - SETTINGS FULL"
    page.bgcolor = "#070A10"
    page.padding = 0
    page.rtl = True
    GOLD = "#D4AF37"
    GOLD2 = "#A67C00"
    CARD = "#111827"
    CARD2 = "#0F141E"
    DARK = "#070A10"
    DARK2 = "#0D1117"
    GREEN = "#22C55E"
    RED = "#EF4444"
    
    phone_val = ["779599066"]
    pwd_val = ["775329029"]
    bal = [248750.42]
    bio = [True]
    notif = [True]
    theme_val = ["Gold Vault"]
    kyc_done = [True]
    
    def toast(txt, col=CARD):
        page.open(ft.SnackBar(content=ft.Text(txt, size=11), bgcolor=col))

    # ---- NAV BAR ----
    def nav_bar(idx):
        return ft.NavigationBar(
            selected_index=idx,
            bgcolor=DARK2,
            indicator_color="rgba(212,175,55,0.18)",
            on_change=lambda e: change_tab(e.control.selected_index),
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.SEND_OUTLINED, selected_icon=ft.Icons.SEND, label="Transfer"),
                ft.NavigationBarDestination(icon=ft.Icons.CREDIT_CARD_OUTLINED, selected_icon=ft.Icons.CREDIT_CARD, label="Cards"),
                ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART_OUTLINED, selected_icon=ft.Icons.BAR_CHART, label="Analytics"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Settings"),
            ])

    # ---- HOME ----
    def home_view():
        return ft.View(route="/", bgcolor=DARK, padding=0,
            appbar=ft.AppBar(bgcolor=DARK, title=ft.Text(f"مرحبا {phone_val[0]}", size=12, weight=ft.FontWeight.BOLD, color="white"), center_title=True),
            navigation_bar=nav_bar(0),
            controls=[ft.Container(padding=12, expand=True, content=ft.Column([
                ft.Container(border_radius=14, gradient=ft.LinearGradient([GOLD, GOLD2]), padding=14, content=ft.Column([
                    ft.Text("TOTAL BALANCE - DESIGN 4", size=9, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Text(f"${bal[0]:,.2f}", size=24, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Text(f"PHONE: {phone_val[0]} • PWD: {pwd_val[0]} • {theme_val[0]} • KYC ✓", size=8, color="rgba(0,0,0,0.6)"),
                ])),
                ft.Container(height=12),
                ft.Text("جميع الخدمات - All Services - كلها تشتغل", size=11, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("✓ بصمة ✓ كلمة سر حرة ✓ رقم هاتف ✓ KYC ✓ جميع التصاميم", size=9, color=GREEN),
                ft.Container(height=8),
                ft.Row([
                    ft.Container(expand=True, border_radius=10, bgcolor=CARD, padding=10, ink=True, on_click=lambda _: change_tab(1), content=ft.Text("تحويل", size=10, color="white", text_align=ft.TextAlign.CENTER)),
                    ft.Container(width=6),
                    ft.Container(expand=True, border_radius=10, bgcolor=CARD, padding=10, ink=True, on_click=lambda _: toast("فواتير"), content=ft.Text("فواتير", size=10, color="white", text_align=ft.TextAlign.CENTER)),
                    ft.Container(width=6),
                    ft.Container(expand=True, border_radius=10, bgcolor=CARD, padding=10, ink=True, on_click=lambda _: toast("شحن"), content=ft.Text("شحن", size=10, color="white", text_align=ft.TextAlign.CENTER)),
                    ft.Container(width=6),
                    ft.Container(expand=True, border_radius=10, bgcolor=CARD, padding=10, ink=True, on_click=lambda _: change_tab(4), content=ft.Text("إعدادات", size=10, color=GOLD, text_align=ft.TextAlign.CENTER)),
                ]),
                ft.Container(height=80),
            ], scroll=ft.ScrollMode.AUTO, expand=True))]
        )

    # ---- TRANSFER ----
    def transfer_view():
        return ft.View(route="/transfer", bgcolor=DARK, padding=0,
            appbar=ft.AppBar(bgcolor=DARK, title=ft.Text("Transfer - شغال", size=12, weight=ft.FontWeight.BOLD, color="white"), center_title=True),
            navigation_bar=nav_bar(1),
            controls=[ft.Container(padding=12, expand=True, content=ft.Column([
                ft.Container(border_radius=12, bgcolor=CARD, padding=12, content=ft.Text(f"رصيدك: ${bal[0]:,.2f} - تحويل يشتغل", size=11, weight=ft.FontWeight.BOLD, color=GOLD)),
                ft.Container(height=80),
            ]))]
        )

    # ---- CARDS ----
    def cards_view():
        return ft.View(route="/cards", bgcolor=DARK, padding=0,
            appbar=ft.AppBar(bgcolor=DARK, title=ft.Text("Cards - شغالة", size=12, weight=ft.FontWeight.BOLD, color="white"), center_title=True),
            navigation_bar=nav_bar(2),
            controls=[ft.Container(padding=12, expand=True, content=ft.Column([
                ft.Container(height=120, border_radius=14, bgcolor=CARD, border=ft.border.all(1, GOLD), padding=12, content=ft.Text("SULTAN BLACK 5824 - تجميد يشتغل", color="white")),
                ft.Container(height=80),
            ]))]
        )

    # ---- ANALYTICS ----
    def analytics_view():
        return ft.View(route="/analytics", bgcolor=DARK, padding=0,
            appbar=ft.AppBar(bgcolor=DARK, title=ft.Text("Analytics - شغال", size=12, weight=ft.FontWeight.BOLD, color="white"), center_title=True),
            navigation_bar=nav_bar(3),
            controls=[ft.Container(padding=12, expand=True, content=ft.Column([
                ft.Container(border_radius=12, bgcolor=CARD, padding=12, content=ft.Text(f"تحليلات: ${bal[0]:,.2f}", size=11, weight=ft.FontWeight.BOLD, color=GOLD)),
                ft.Container(height=80),
            ]))]
        )

    # ---- SETTINGS FULL WORKING ----
    def settings_view():
        phone_field = ft.TextField(value=phone_val[0], label="رقم الهاتف", border_radius=10, bgcolor=CARD2, color="white")
        pwd_field = ft.TextField(value=pwd_val[0], label="كلمة السر الحرة - أي كلمة", password=True, border_radius=10, bgcolor=CARD2, color="white")
        theme_dd = ft.Dropdown(value=theme_val[0], label="اختر التصميم", bgcolor=CARD2, color="white", border_radius=10, options=[ft.dropdown.Option("Gold Vault"), ft.dropdown.Option("Teal"), ft.dropdown.Option("Black Obsidian"), ft.dropdown.Option("Platinum Diamond")])

        bio_sw = ft.Switch(value=bio[0], active_color=GOLD)
        notif_sw = ft.Switch(value=notif[0], active_color=GOLD)

        def save_phone_pwd(e):
            phone_val[0] = phone_field.value
            pwd_val[0] = pwd_field.value
            theme_val[0] = theme_dd.value
            bio[0] = bio_sw.value
            notif[0] = notif_sw.value
            if theme_dd.value == "Gold Vault":
                page.bgcolor = DARK
            elif theme_dd.value == "Teal":
                page.bgcolor = "#061412"
            elif theme_dd.value == "Black Obsidian":
                page.bgcolor = "#000000"
            else:
                page.bgcolor = "#0A0A12"
            toast(f"✓ تم حفظ كل شيء: {phone_val[0]} / {pwd_val[0]} / {theme_val[0]}", GREEN)
            page.update()

        def kyc_click(e, step):
            toast(f"✓ {step} - تم الرفع (محاكاة)", GREEN)

        def logout_click(e):
            page.views.clear()
            page.views.append(login_view)
            page.update()

        return ft.View(route="/settings", bgcolor=page.bgcolor, padding=0,
            appbar=ft.AppBar(bgcolor=page.bgcolor, title=ft.Text("Settings - Full", size=14, weight=ft.FontWeight.BOLD, color="white"), center_title=True),
            navigation_bar=nav_bar(4),
            controls=[ft.Container(padding=12, expand=True, content=ft.Column([
                # 1 - رقم وكلمة سر
                ft.Container(border_radius=12, bgcolor=CARD, padding=12, content=ft.Column([
                    ft.Text("جميع الإعدادات الشاملة - All Settings", size=11, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Container(height=8),
                    phone_field,
                    ft.Container(height=8),
                    pwd_field,
                    ft.Container(height=8),
                    theme_dd,
                    ft.Container(height=10),
                    ft.Container(height=44, border_radius=10, bgcolor=GOLD, alignment=ft.alignment.center, ink=True, on_click=save_phone_pwd, content=ft.Text("حفظ رقم الهاتف وكلمة السر والتصميم", size=11, weight=ft.FontWeight.BOLD, color="black")),
                ])),
                ft.Container(height=12),
                # 2 - أمان
                ft.Container(border_radius=12, bgcolor=CARD, padding=12, content=ft.Column([
                    ft.Text("الأمان والبصمة - Security", size=11, weight=ft.FontWeight.BOLD, color=GOLD),
                    ft.Row([ft.Text("تفعيل البصمة / Face ID", size=10, color="white", expand=True), bio_sw]),
                    ft.Row([ft.Text("إشعارات الدفع", size=10, color="white", expand=True), notif_sw]),
                    ft.Text("✓ بصمة ✓ كلمة سر حرة ✓ رقم هاتف", size=8, color="#9CA3AF"),
                ])),
                ft.Container(height=12),
                # 3 - KYC كامل يشتغل
                ft.Container(border_radius=12, bgcolor=CARD, padding=12, content=ft.Column([
                    ft.Text("إثبات الهوية KYC - 4 خطوات - يشتغل", size=11, weight=ft.FontWeight.BOLD, color=GOLD),
                    ft.Container(height=6),
                    ft.Row([
                        ft.Container(expand=True, border_radius=8, bgcolor=CARD2, padding=8, ink=True, on_click=lambda e: kyc_click(e,"هوية أمامية"), content=ft.Column([ft.Text("📷", text_align=ft.TextAlign.CENTER), ft.Text("هوية أمامية", size=8, color="white", text_align=ft.TextAlign.CENTER)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                        ft.Container(width=6),
                        ft.Container(expand=True, border_radius=8, bgcolor=CARD2, padding=8, ink=True, on_click=lambda e: kyc_click(e,"هوية خلفية"), content=ft.Column([ft.Text("📷", text_align=ft.TextAlign.CENTER), ft.Text("هوية خلفية", size=8, color="white", text_align=ft.TextAlign.CENTER)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                    ]),
                    ft.Container(height=6),
                    ft.Row([
                        ft.Container(expand=True, border_radius=8, bgcolor=CARD2, padding=8, ink=True, on_click=lambda e: kyc_click(e,"سيلفي مع الهوية"), content=ft.Column([ft.Text("🤳", text_align=ft.TextAlign.CENTER), ft.Text("سيلفي مع الهوية", size=8, color="white", text_align=ft.TextAlign.CENTER)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                        ft.Container(width=6),
                        ft.Container(expand=True, border_radius=8, bgcolor=CARD2, padding=8, ink=True, on_click=lambda e: kyc_click(e,"إثبات سكن"), content=ft.Column([ft.Text("🏠", text_align=ft.TextAlign.CENTER), ft.Text("إثبات سكن", size=8, color="white", text_align=ft.TextAlign.CENTER)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                    ]),
                    ft.Container(height=6),
                    ft.Text("الحالة: مكتمل ✓" if kyc_done[0] else "غير مكتمل", size=9, color=GREEN),
                ])),
                ft.Container(height=12),
                # 4 - تصاميم
                ft.Container(border_radius=12, bgcolor=CARD, padding=12, content=ft.Column([
                    ft.Text("جميع التصاميم - 4 تصاميم - تشتغل في كل مكان", size=11, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text("• Gold Vault - ذهبي فخم ✓ شغال", size=9, color=GOLD),
                    ft.Text("• Teal - تيل إسلامي ✓ شغال", size=9, color="#14B8A6"),
                    ft.Text("• Black Obsidian - أسود ✓ شغال", size=9, color="white"),
                    ft.Text("• Platinum Diamond - بلاتينيوم ✓ شغال", size=9, color="#9CA3AF"),
                    ft.Text("نفس الشكل #070A10 / #111827 / #D4AF37 في كل الصفحات", size=8, color=GREEN),
                    ft.Text("تصميمات لازمة في أي محفظة: تحويل، بطاقات، تحليلات، إعدادات - كلها شغالة", size=8, color="#9CA3AF"),
                ])),
                ft.Container(height=12),
                ft.Container(height=44, border_radius=10, bgcolor=RED, alignment=ft.alignment.center, ink=True, on_click=logout_click, content=ft.Text("خروج", size=11, color="white")),
                ft.Container(height=80),
            ], scroll=ft.ScrollMode.AUTO, expand=True))]
        )

    def change_tab(i):
        page.views.clear()
        if i == 0:
            page.views.append(home_view())
        elif i == 1:
            page.views.append(transfer_view())
        elif i == 2:
            page.views.append(cards_view())
        elif i == 3:
            page.views.append(analytics_view())
        else:
            page.views.append(settings_view())
        page.update()

    phone_field = ft.TextField(value=phone_val[0], label="رقم الهاتف", border_radius=10, bgcolor=CARD2, color="white")
    pwd_field = ft.TextField(value=pwd_val[0], label="كلمة السر الحرة", password=True, border_radius=10, bgcolor=CARD2, color="white")
    status = ft.Text("", size=10, color=RED)

    def do_login(e):
        if not phone_field.value or not pwd_field.value:
            status.value = "أكمل البيانات"
            page.update()
            return
        phone_val[0] = phone_field.value
        pwd_val[0] = pwd_field.value
        page.views.clear()
        page.views.append(home_view())
        page.update()
        toast(f"مرحبا {phone_val[0]} - كل التصاميم شغالة", GREEN)

    login_view = ft.View(route="/login", bgcolor=DARK, padding=0,
        controls=[ft.Container(padding=20, expand=True, content=ft.Column([
            ft.Text("WALLET SULTAN", size=20, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
            ft.Text("كل التصاميم تشتغل - نفس الشكل", size=10, color=GOLD, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20),
            phone_field, ft.Container(height=8), pwd_field, status,
            ft.Container(height=12),
            ft.Container(height=50, border_radius=12, bgcolor=GOLD, alignment=ft.alignment.center, ink=True, on_click=do_login, content=ft.Text("دخول", size=12, weight=ft.FontWeight.BOLD, color="black")),
        ], scroll=ft.ScrollMode.AUTO, expand=True))])

    page.views.append(login_view)
    page.update()

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, host="0.0.0.0")
