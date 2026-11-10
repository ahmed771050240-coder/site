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

- `main.py` — Flet Android demonstration client.
- `backend/main.py` — FastAPI authentication and read-only wallet API.
- `migrations/001_init.sql` — PostgreSQL schema.
- `requirements-server.txt` — backend dependencies.
- `.github/workflows/build-apk.yml` — Android APK build.

## Build Android APK

The GitHub Actions workflow builds the Flet APK for arm64-v8a. Run it from Actions or push a change to `main`. Download the APK from the successful workflow's Artifacts section.

## Run the backend

1. Create a PostgreSQL database.
2. Apply `migrations/001_init.sql`.
3. Install dependencies: `pip install -r requirements-server.txt`.
4. Set `DATABASE_URL` and `JWT_SECRET_KEY` in the server environment. Use a random secret of at least 32 characters.
5. Start: `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.

See [backend/README.md](backend/README.md) and [SECURITY.md](SECURITY.md).

## Production readiness still required

Before accepting real money: licensed provider contracts, KYC/AML vendor and operations, double-entry immutable ledger, idempotency, provider settlement and signed webhooks, reconciliation, MFA, rate limiting, refresh-token revocation, admin RBAC, audit monitoring, backups, privacy controls, penetration testing, and legal/regulatory approval.

A target sale price of USD 10,000 is a commercial goal, not a guaranteed valuation. Buyers will expect a working build, test evidence, documentation, clear IP ownership, and proof of provider/licensing readiness.


## Build status
The Android APK is produced by the GitHub Actions workflow after a push to `main` or a manual workflow run. A successful run publishes the APK as the `SULTAN-WALLET-APK` artifact.
