from pathlib import Path

p = Path("main.py")
s = p.read_text(encoding="utf-8")

if "def show_login_options" in s:
    print("خيارات الدخول موجودة مسبقًا. لم يتم إجراء أي تعديل.")
    raise SystemExit

needle = '    lock_screen = ft.Container('
if needle not in s:
    print("لم أجد شاشة القفل في المكان المتوقع. لم يتم تعديل main.py.")
    raise SystemExit

insert = '''    def show_login_options(e=None):
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

        def show_message(message):
            page.open(ft.SnackBar(content=ft.Text(message)))

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
                            on_click=lambda e: show_message(
                                "لم يتم ربط تسجيل الدخول بالخادم بعد؛ لم تُرسل بياناتك."
                            ),
                        ),
                        ft.Button(
                            "إنشاء حساب جديد",
                            width=300,
                            on_click=lambda e: show_message(
                                "إنشاء الحساب يحتاج ربط قاعدة بيانات وخادم آمن."
                            ),
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
                            on_click=lambda e: page.launch_url(
                                "https://wa.me/967779599066"
                            ),
                        ),
                        ft.TextButton(
                            "العودة إلى شاشة PIN",
                            on_click=lambda e: (
                                page.controls.clear(),
                                page.add(lock_screen),
                                page.update()
                            ),
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

'''
s = s.replace(needle, insert + needle, 1)

old = 'on_click=check_pin,'
new = 'on_click=show_login_options,'
if old not in s:
    print("لم أجد زر الدخول المتوقع. لم يتم تعديل main.py.")
    raise SystemExit

s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("تمت إضافة واجهة خيارات الدخول إلى main.py.")
print("تنبيه: الواجهة تجريبية حتى ربط الخادم وقاعدة البيانات.")
