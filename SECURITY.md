# Security and financial-safety policy

- The Android client is a demonstration interface, not a source of truth for balances.
- Never credit a wallet because a user tapped a button or supplied a screenshot.
- Deposits and withdrawals must be confirmed server-to-server by a licensed provider.
- Transfers must use atomic ledger postings, idempotency keys, settlement states, and reconciliation.
- Provider webhooks must have signature verification, replay protection, and durable event storage.
- Never store card PAN/CVV data in this project. Use tokenization from a compliant card issuer.
- KYC documents and identity numbers must not be collected until encrypted storage, access controls, retention/deletion procedures, and an authorized review process are in place.
- Keep all production secrets outside Git and outside the APK.
- Obtain legal advice and required licenses before offering financial services.
