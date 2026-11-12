# SULTAN WALLET — Reown AppKit connector

## Configuration

- Reown Project ID: `d49f5ad010ca1d1451ec6eff23e61e0e`
- Flutter package: `reown_appkit: ^1.9.0`
- Deep-link scheme: `sultanwallet://`
- Supported wallet discovery: MetaMask and Trust Wallet through Reown / WalletConnect.

The Project ID is a public application identifier. Never place private keys, recovery phrases, signing secrets, or user credentials in this project.

## Bridge implementation

The Android client is a Flet 1.0.5 application, so the connector is implemented as a Flet Flutter extension rather than importing the native Kotlin SDK into Python:

- Python control: `src/sultan_wallet_reown/`
- Flutter extension: `src/flutter/sultan_wallet_reown/`
- Reown AppKit modal: `ReownAppKitModal`
- Android return links: Flutter `app_links` stream, with Flet's Android deep-link manifest configuration.
- Wallet state sent to Python: public address, connected wallet display name, and selected chain ID.
- UI: connect modal before connection; account control after connection.

The Python app displays the connector on its home screen. The Flutter control handles wallet connection and dispatches connection, disconnection, and error events back to Python.

## Security boundaries

- The app never asks for, reads, stores, or transmits a recovery phrase or private key.
- The app does not sign or submit transactions automatically.
- Any transaction or signature request must be presented by the wallet and explicitly approved by the user.
- A connected wallet is not a bank account and does not enable fiat deposits, withdrawals, card issuing, or bank transfers.

## Build and verification status

The connector source and APK build configuration are committed on branch `fix/android-ui-stability`. The GitHub Actions workflow includes this branch and the extension source paths.

**Not yet verified in a built APK or on a physical Android device.** Before describing the feature as production-ready, build the APK and test:
1. AppKit initialization with the configured Project ID.
2. MetaMask connection and return-to-app deep link.
3. Trust Wallet connection and return-to-app deep link.
4. Account and chain display after connection.
5. User cancellation, rejected connection, disconnect, app restart, and reconnect.

## Official references

- Reown Flutter AppKit: https://pub.dev/packages/reown_appkit
- Reown Flutter examples: https://github.com/reown-com/reown_flutter
- Flet extensions: https://flet.dev/docs/extend/user-extensions/
- Flet Android deep links: https://flet.dev/docs/publish/
