# Backend foundation

## Current scope
- PostgreSQL-backed registration and login.
- Argon2 password hashing and short-lived signed access tokens.
- Read-only account balances for SAR, USD, AED, and YER.
- Explicit capability flags showing that money movement is disabled.

No endpoint can create deposits, withdrawals, transfers, card credentials, or completed top-up orders. Do not enable those features by editing a client-side balance.

## Run locally
1. Create a PostgreSQL database.
2. Apply `migrations/001_init.sql`.
3. Install `requirements-server.txt`.
4. Set `DATABASE_URL` and a random `JWT_SECRET_KEY` of at least 32 characters in the server environment.
5. Run `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.

Keep the API behind HTTPS and a reverse proxy. Never put database credentials or JWT secrets in the APK or commit them to Git.

## Before production
Add provider-backed KYC/AML, rate limiting, MFA, refresh-token rotation/revocation, device/session controls, immutable double-entry journal, idempotency keys, atomic provider settlement, signed webhook verification, reconciliation, admin RBAC, alerting, backups, privacy retention rules, penetration testing, and legal/regulatory review. The current backend is a foundation, not a licensed financial service.


## Android client integration

The Android app calls `/auth/register`, `/auth/login`, `/me`, and `/wallets` over HTTPS. Access tokens remain in memory for the current app session; signing in again is required after a restart. The client never writes server wallet balances locally.

The app intentionally keeps transfers, deposits, withdrawals, KYC approval, card issuing, and service fulfillment disabled. The current API reports demo balances and does not represent customer funds.
