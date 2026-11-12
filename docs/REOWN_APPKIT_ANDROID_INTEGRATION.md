# SULTAN WALLET — Reown AppKit integration

## Project configuration

- Reown Project ID: `d49f5ad010ca1d1451ec6eff23e61e0e`
- Product: SULTAN WALLET
- Intended Android package: `org.sultan.wallet`
- Wallets: MetaMask and Trust Wallet through the WalletConnect network.

The Project ID is a public application identifier. Never put private keys, recovery phrases, signing secrets, or user credentials in this file or in the app.

## Current client architecture

The Android client in this repository is a Python/Flet application (Flet 1.0.5). Reown's Android AppKit is a native Kotlin SDK; adding its Maven dependency to the Python requirements or placing the Project ID in Python does **not** integrate the SDK. The current Flet APK workflow does not compile a custom Kotlin Activity/Fragment or provide a verified method-channel bridge.

## Required implementation before enabling the feature

1. Add a native Android host/bridge that is actually included by the APK build.
2. Integrate the official Reown Android AppKit SDK using its current Android BOM and documented initialization API.
3. Configure the app metadata and a unique native redirect URI; register the matching Android intent filter.
4. Expose only safe bridge methods to Flet: connect, current account, chain, disconnect, and connection state.
5. Route WalletConnect deep links back to AppKit and dispatch them to the SDK.
6. Never request, read, store, or transmit a wallet recovery phrase or private key.
7. Do not submit transactions automatically. Any signing or transaction request must be shown to the user and explicitly approved in MetaMask/Trust Wallet.
8. Add tests for connect, cancel/reject, reconnect, disconnect, unsupported chain, and malformed deep links.

## Feature status

**Not enabled in the production Flet APK yet.** This file records the supplied public Project ID and the verified integration boundary. Do not display a successful connection state until the native bridge has been built and device-tested.

## Official references

- Reown Android/Kotlin SDK: https://github.com/reown-com/reown-kotlin
- Reown AppKit overview and framework support: https://docs.reown.com/
- WalletConnect app integration overview: https://docs.walletconnect.com/apps
