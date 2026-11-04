import flet as ft
import requests

API_URL = "http://127.0.0.1:8000"

def main(page: ft.Page):
    page.title = "محفظة سلطان - Sultan Wallet"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 700

    current_user = {"username": "", "balance": 0.0}

    username_field = ft.TextField(label="اسم المستخدم", icon=ft.icons.PERSON, width=300)
    password_field = ft.TextField(label="كلمة المرور", password=True, can_reveal_password=True, width=300)
    status_text = ft.Text("", color=ft.colors.RED_ACCENT)

    receiver_field = ft.TextField(label="اسم المستلم", icon=ft.icons.SEND, width=300)
    amount_field = ft.TextField(label="المبلغ", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    wallet_status = ft.Text("")
    balance_display = ft.Text("الرصيد: $0.0", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN)

    def show_wallet_view():
        page.clean()
        balance_display.value = f"الرصيد الحالي: ${current_user['balance']}"

        def handle_transfer(e):
            try:
                res = requests.post(f"{API_URL}/transfer", json={
                    "sender": current_user["username"],
                    "receiver": receiver_field.value,
                    "amount": float(amount_field.value)
                })
                data = res.json()
                if res.status_code == 200:
                    wallet_status.value = data["message"]
                    wallet_status.color = ft.colors.GREEN
                    current_user["balance"] -= float(amount_field.value)
                    balance_display.value = f"الرصيد الحالي: ${current_user['balance']}"
                else:
                    wallet_status.value = data.get("detail", "حدث خطأ في التحويل")
                    wallet_status.color = ft.colors.RED_ACCENT
            except Exception as ex:
                wallet_status.value = f"خطأ في الاتصال: {ex}"
                wallet_status.color = ft.colors.RED_ACCENT
            page.update()

        page.add(
            ft.Column([
                ft.Text(f"أهلاً بك يا أبو سلطان 🦅", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"المستخدم: {current_user['username']}", size=16),
                balance_display,
                ft.Divider(),
                ft.Text("إرسال أموال", size=18, weight=ft.FontWeight.BOLD),
                receiver_field,
                amount_field,
                ft.ElevatedButton("إرسال الآن", on_click=handle_transfer, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE),
                wallet_status,
                ft.ElevatedButton("تسجيل خروج", on_click=lambda _: show_login_view(), bgcolor=ft.colors.RED),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        )
        page.update()

    def login_click(e):
        try:
            res = requests.post(f"{API_URL}/login", json={
                "username": username_field.value,
                "password": password_field.value
            })
            data = res.json()
            if res.status_code == 200:
                current_user["username"] = data["username"]
                current_user["balance"] = data["balance"]
                show_wallet_view()
            else:
                status_text.value = data.get("detail", "فشل تسجيل الدخول")
        except Exception as ex:
            status_text.value = f"لا يمكن الاتصال بالسيرفر: {ex}"
        page.update()

    def register_click(e):
        try:
            res = requests.post(f"{API_URL}/register", json={
                "username": username_field.value,
                "password": password_field.value
            })
            data = res.json()
            if res.status_code == 200:
                status_text.value = "تم إنشاء الحساب بنجاح! سجل دخولك الآن."
                status_text.color = ft.colors.GREEN
            else:
                status_text.value = data.get("detail", "خطأ في التسجيل")
                status_text.color = ft.colors.RED_ACCENT
        except Exception as ex:
            status_text.value = f"خطأ في الاتصال: {ex}"
            status_text.color = ft.colors.RED_ACCENT
        page.update()

    def show_login_view():
        page.clean()
        page.add(
            ft.Column([
                ft.Text("Sultan Wallet 👑", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER),
                ft.Text("تسجيل الدخول أو إنشاء حساب جديد", size=14),
                username_field,
                password_field,
                ft.Row([
                    ft.ElevatedButton("دخول", on_click=login_click, bgcolor=ft.colors.GREEN, color=ft.colors.WHITE),
                    ft.ElevatedButton("إنشاء حساب", on_click=register_click, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER),
                status_text,
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        )
        page.update()

    show_login_view()

ft.app(target=main)
