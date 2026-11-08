# SULTAN WALLET — UI refresh 1.1.0

This package contains the updated Flet Android app source.

## Changes
- Replaced the previous wallet dashboard presentation with the dark emerald SULTAN WALLET interface.
- Preserved the existing login, registration, API endpoints, account details, and live wallet/transaction retrieval.
- Kept transfer, deposit, withdrawal, and report actions clearly marked as unavailable until their secure backend flows are implemented.
- APK workflow remains configured for arm64-v8a and excludes server-side secrets and files.

## Build
The GitHub Actions workflow `.github/workflows/build-apk.yml` builds the Android APK when run manually or when relevant source files are pushed.

Do not include `wallet_auth.db`, `auth_secret.key`, or other server secrets in the Android package.


## Upgrade work in progress

- Added separate horizontally scrollable wallet balance cards in this order: SAR, USD, AED, YER.
- Added AED to the internal wallet ledger currency set. Existing users receive the AED account when their wallet endpoint next initializes its account rows.
- Added `/market/fx` using Frankfurter daily reference rates and `/market/gold` using XAUS spot data. The app displays source dates/status and does not invent missing values.
- Added UI placeholders for international transfers, app top-ups and game credits. These are not enabled for real purchases until licensed providers and server-side payment verification are integrated.

## Important production limitations

The current transfer ledger is an internal demonstration balance only (`real_money_enabled: false`). It is not connected to banks, card processors, remittance networks, app-store top-up providers, or KYC/AML verification. Market reference rates are not executable local exchange quotes. Gold spot data is indicative and may be delayed or unavailable. Do not use the current build to hold or transfer customer funds.
