# SULTAN WALLET — OTA foundation

This branch introduces a remote web interface served by the API and a thin Android WebView shell. UI and web/API releases can be deployed server-side without replacing the APK. Android-native capabilities, permissions, package identity, and shell changes still require an APK update.

## Important financial status

- Wallet balances are internal ledger balances only.
- `real_money_enabled` is always false.
- No cash deposits, withdrawals, card issuing, SMS verification, remittances, or licensed payment-provider integration is implemented.
- Do not advertise these as live financial services until a licensed provider is contracted, configured, and independently tested.

## Render deployment requirements

Configure these environment variables on the existing Render web service before deploying this branch:

- `DATABASE_URL`: the connection string for a persistent Render PostgreSQL database. Use the internal connection URL when the database and service are in the same Render region. Do not paste it into GitHub or chat.
- `JWT_SECRET`: a random secret of at least 32 bytes. Keep it private and persistent; changing it invalidates existing sessions.

The service start command is `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. The API applies the initial schema migration at startup and the health check returns healthy only when PostgreSQL and required tables are available.

### Existing SQLite data

This branch does not automatically import any SQLite data. Before switching production traffic, take a backup and perform a separately verified migration if there are existing user records that must be retained. Do not delete the old service or database until reconciliation is complete.

## Validation sequence

1. Configure persistent PostgreSQL and the two environment variables in Render.
2. Deploy this branch to a staging service first.
3. Verify `/health`, registration, login, `/me`, zero-initialized balances, and transaction history.
4. Test an internal transfer with two test accounts and verify both account balances and both ledger entries.
5. Confirm failed/duplicate transfers do not debit either account.
6. Only then point the Android shell at the verified HTTPS service and build/install the one-time shell update.

## OTA limits

Remote HTML/CSS/JavaScript and server-side API behavior can be updated on the hosted service. Changes to Android native code, permissions, signing, package ID, or the embedded Flet shell require a new APK. The same Android application ID and signing key must be retained for in-place upgrades.
