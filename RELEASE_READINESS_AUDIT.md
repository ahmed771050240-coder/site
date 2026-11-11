# SULTAN WALLET — Release Readiness Audit

Audit target: default-branch commit `a023336cfe62d00ba374c65d168de79744eec119` (2026-11-11).

## Decision

**NOT READY for production banking, real-money operation, or sale as a complete working wallet.** The current code is a demo foundation. Do not describe local balances, transfer screens, service catalogues, or displayed FX rates as completed financial services.

## Verified release blockers

1. The Android UI in root `main.py` creates and uses a local SQLite database for users, accounts and ledger. It does not call the PostgreSQL API in `backend/main.py`.
2. Registration and login in the Android UI are local-only and are not backed by the production API.
3. `do_transfer`, `topup`, `buy_service`, and `do_kyc` explicitly stop and report that these actions are unavailable.
4. The transfer selector advertises local bank and SWIFT transfers, but no bank/payment provider integration is present.
5. The service catalogue lists operators and products, but fulfillment is disabled.
6. `backend/main.py` explicitly returns `money_movement_enabled: false` and exposes no deposit, withdrawal, transfer, card-issuing, KYC-review, or service-fulfillment endpoints.
7. `.github/workflows/build-flet-apk.yml` compiles Python source and packages an APK. It does not run PostgreSQL integration tests, install the APK, or exercise Android UI flows.
8. The app's displayed demo balances must never be represented as real funds.

## Required implementation and verification

- Choose one backend and make it the sole source of truth; connect the Android app to it over HTTPS with authenticated API calls.
- Remove client-side balance mutation. All financial ledger changes must be server-side, atomic, auditable, idempotent and reconciled.
- Add PostgreSQL integration tests covering registration, login, authorization, wallet reads, transfer invariants, concurrency, idempotency, rollback and ledger balance.
- Add Android arm64 build validation plus emulator/device smoke tests for startup, registration, login, navigation, API failure handling and session expiry.
- Implement deposits, withdrawals, domestic/international transfers and service fulfillment only through contracted, licensed providers with verified webhooks, settlement and reconciliation.
- Complete compliant KYC/AML, MFA, recovery, admin RBAC, audit logging, monitoring, backup/restore and independent security testing.
- Verify provider credentials, deployment configuration, privacy/legal requirements and release documentation before commercial release.

## Environment and external dependencies still required

Real-money provider credentials/contracts, production database and secrets, KYC/AML provider, card issuer (if cards are offered), deployment access, and a physical Android device or emulator are not available to this source audit. Never paste secrets into Git or chat; configure them through the hosting provider's secret manager.

## Release acceptance rule

A successful APK build alone is not a release pass. Mark this project production-ready only after the above tests pass against the release commit and provider sandbox/production certification is documented. Until then, label it clearly as a demo/showcase prototype.
