from kivy.app import App
from kivy.uix.label import Label

class SultanWallet(App):
    def build(self):
        return Label(
            text="SULTAN WALLET\n\nمحفظتك الرقمية",
            font_size=28
        )

SultanWallet().run()

