# SULTAN WALLET — Core wallet build

This source keeps the dark emerald/gold visual direction and adds working account, wallet, internal-transfer, transaction-history, wallet-summary and account/settings screens.

## Current working scope
- Phone/password registration and login against the FastAPI service.
- Password hashes use PBKDF2-HMAC-SHA256 (600,000 iterations); session tokens are signed and expire after one hour.
- Wallet accounts are created for YER, SAR, AED and USD with zero opening balance.
- Internal user-to-user transfers debit and credit server-side in one database transaction, enforce available balance, use unique idempotency keys, and write double-entry ledger rows plus an audit event.
- Transaction history is read from the server database.
- UI never reports external deposits, withdrawals, cards or bank transfers as completed.

## Important limitations — not ready for commercial money movement
- `real_money_enabled` is deliberately `false`. Internal balances are not bank deposits, stored value, or cash and have no external funding/withdrawal rail.
- No public endpoint exists to credit a wallet. Do not add one without a verified payment-provider webhook, signature validation, reconciliation and idempotency.
- Deposits, withdrawals, virtual cards, international transfers, SMS OTP, KYC, 2FA, push notifications, customer support ticketing and admin console require additional implementation and/or regulated providers.
- A production deployment must use a managed PostgreSQL database. Set `DATABASE_URL` to its private connection string and `AUTH_SECRET` to a random secret of at least 32 characters. The local SQLite fallback is for development only and is not durable on ephemeral hosting.
- Before commercial launch, obtain legal/regulatory advice and the required e-money/payment licenses for each target country, complete AML/KYC, sanctions screening, safeguarding, privacy, dispute and incident-response procedures, and obtain provider approval.

## Backend deployment
1. Deploy this folder as a Render web service using `render.yaml`.
2. Create a managed PostgreSQL database and set its private connection string as `DATABASE_URL`.
3. Ensure `AUTH_SECRET` is set to a long random value (Render can generate one).
4. Confirm `GET /health` reports PostgreSQL, not SQLite.
5. Never place server secrets or database files in the Android package or Git repository.

## Android build
The GitHub Actions workflow builds an arm64-v8a APK. Push the project to the configured GitHub repository and run the workflow manually. Build success is not claimed until CI completes and the APK is installed and tested on a real device.

## Stage 4 — internal transfer hardening (1.2.4)
- A transfer retry with the same idempotency key and identical recipient/currency/amount returns the original reference without a second debit.
- Reusing an idempotency key with a different amount, currency or recipient returns HTTP 409.
- Test coverage verifies funded internal transfers, sender debit, receiver credit, two ledger entries, sender/receiver history, insufficient-funds rejection and database-unavailable readiness behavior.
- Internal transfer API: `POST /wallet/transfers` (Bearer token required). Wallet summary: `GET /wallet`. History: `GET /wallet/transactions`.
- Test fixtures may seed balances directly in an isolated local test database only. There is intentionally no public balance-credit endpoint.
- External transfers are not enabled in this stage. They require a licensed provider, approved corridors, compliance checks, signed webhooks, reconciliation and provider-side end-to-end tests.


## Wallet screen update 1.2.5

- Improved the wallet screen with separate YER, SAR, AED, and USD account cards.
- Added an explicit refresh action and loading/error messaging.
- Added quick navigation to internal transfers and transaction history.
- Added recent wallet activity and clear disclosure that balances are internal ledger balances, not bank deposits.
- Deposit and withdrawal remain unavailable until a licensed payment provider is integrated and tested.
- Currency balances are intentionally not summed into a single total without a trusted FX quote.
