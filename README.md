# SULTAN WALLET

SULTAN WALLET is a multi-currency wallet application prototype with separate SAR, USD, AED, and YER account views.

## Current product status

This repository is a software prototype and backend foundation. It is **not a bank, e-money institution, card issuer, remittance provider, or licensed payment service**.

- The Android app is a demonstration UI. Local balances are not customer funds.
- Deposits, withdrawals, transfers, card issuing, and service fulfillment are disabled until licensed providers and secure server-side integrations are contracted and tested.
- The API supports registration, login, and read-only demo wallet accounts.
- FX figures, if displayed by a client, are indicative reference data and not executable exchange quotes.
- KYC is not approved automatically. Do not collect real identity documents until secure backend storage and an authorized review workflow exist.

## Repository layout

- `main.py` — Flet Android client; registration, login, profile, and wallet reads use the HTTPS API.
- `wallet_api.py` — small HTTPS API client; no client-side balance mutation.
- `backend/main.py` — FastAPI authentication and read-only wallet API.
- `migrations/001_init.sql` — PostgreSQL schema.
- `requirements-server.txt` — backend dependencies.
- `.github/workflows/build-apk.yml` — Android APK build.

## Build Android APK

The GitHub Actions workflow builds the Flet APK for arm64-v8a. Run it from Actions or push a change to `main`. Download the APK from the successful workflow's Artifacts section.

## Deploy the backend

The Render Blueprint starts `backend.main:app` (not the legacy `auth_server.py`). Before first use:

1. Create/attach a PostgreSQL database and set `DATABASE_URL` in the service environment.
2. Apply `migrations/001_init.sql` to that database.
3. Set `JWT_SECRET_KEY` to a cryptographically random secret of at least 32 characters.
4. Deploy the service and confirm `/health` reports `status: ok` and `database: ready`. Health now fails if the secret, database, or required tables are missing.
5. The Android client defaults to `https://sultan-wallet-api.onrender.com`; override `SULTAN_WALLET_API_URL` only when building for a different HTTPS API.

For local development, install dependencies and run `uvicorn backend.main:app --host 127.0.0.1 --port 8000` after applying the migration.

See [backend/README.md](backend/README.md) and [SECURITY.md](SECURITY.md).

## Production readiness still required

Before accepting real money: licensed provider contracts, KYC/AML vendor and operations, double-entry immutable ledger, idempotency, provider settlement and signed webhooks, reconciliation, MFA, rate limiting, refresh-token revocation, admin RBAC, audit monitoring, backups, privacy controls, penetration testing, and legal/regulatory approval.

A target sale price of USD 10,000 is a commercial goal, not a guaranteed valuation. Buyers will expect a working build, test evidence, documentation, clear IP ownership, and proof of provider/licensing readiness.


## Build status
The Android APK is produced by the GitHub Actions workflow after a push to `main` or a manual workflow run. A successful run publishes the APK as the `SULTAN-WALLET-APK` artifact.
