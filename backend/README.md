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


## Email verification setup (Microsoft Outlook)

The API now exposes authenticated email OTP endpoints:
- `POST /auth/email/request-code` with JSON `{"email":"user@example.com"}`
- `POST /auth/email/verify-code` with JSON `{"code":"123456"}`
- `GET /auth/email/status`

All three require the user's Bearer access token. Codes expire after 10 minutes, are stored as hashes, allow at most 5 attempts, and are limited to 3 requests per account per hour.

### Microsoft Graph configuration

Outlook.com requires OAuth2/Modern Authentication; a mailbox password or basic SMTP login is not supported. Create a Microsoft app registration for personal Microsoft accounts, enable public-client/device-code flow, and grant Microsoft Graph delegated `Mail.Send`. Then run `scripts/get_microsoft_refresh_token.py` locally with `MS_CLIENT_ID` set. Complete the Microsoft device sign-in and copy the resulting refresh token directly into the Render secret environment; never commit it or send it in chat.

Set these Render environment variables:
- `MS_CLIENT_ID` — Microsoft app registration Application (client) ID.
- `MS_REFRESH_TOKEN` — refresh token from the one-time setup script.
- `SULTAN_EMAIL_FROM` — optional reply-to address, normally `sultanwallet@outlook.sa`.

The API uses Microsoft Graph `/me/sendMail`. The actual From address is the Microsoft mailbox authorized during OAuth; an Outlook alias is not guaranteed to be the From address. Verify the delivered message's From field before treating the sender branding as complete.

### Database migration

Apply `migrations/002_email_verification.sql` to the same PostgreSQL database after `001_init.sql` and before using the email endpoints. The Android client must also be connected to these API routes; the current Flet client still contains local SQLite registration/login and does not yet invoke these OTP endpoints.
