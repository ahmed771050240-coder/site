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
