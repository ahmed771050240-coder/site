"""SULTAN WALLET Android shell.

The application shell stays installed; the authenticated web experience is served
over HTTPS so UI/content releases can be deployed without replacing the APK.
Native capabilities and shell changes still require an APK update.
"""
import flet as ft
import flet_webview as fwv

REMOTE_APP_URL = "https://sultan-wallet-api.onrender.com/app"


def main(page: ft.Page):
    page.title = "SULTAN WALLET"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#080D19"
    page.padding = 0
    page.spacing = 0

    webview = fwv.WebView(
        url=REMOTE_APP_URL,
        expand=True,
        bgcolor="#080D19",
        on_web_resource_error=lambda e: print("SULTAN WALLET web error:", e.data),
    )
    page.add(ft.SafeArea(content=webview, expand=True))


if __name__ == "__main__":
    ft.run(main)
