from typing import Optional

import flet as ft


@ft.control("sultan_wallet_reown")
class SultanWalletReown(ft.LayoutControl):
    """Secure Reown AppKit wallet connector for MetaMask and Trust Wallet.

    The control only exposes the public account address, chain ID and wallet
    display name. It never reads or stores recovery phrases or private keys.
    """

    project_id: str = "d49f5ad010ca1d1451ec6eff23e61e0e"
    on_wallet_connected: Optional[ft.EventHandler[ft.ControlEvent]] = None
    on_wallet_disconnected: Optional[ft.EventHandler[ft.ControlEvent]] = None
    on_wallet_error: Optional[ft.EventHandler[ft.ControlEvent]] = None
