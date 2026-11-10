-- Apply with: psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f migrations/001_init.sql
CREATE TABLE IF NOT EXISTS app_users (
    id BIGSERIAL PRIMARY KEY,
    phone VARCHAR(24) NOT NULL UNIQUE,
    full_name VARCHAR(120) NOT NULL,
    password_hash TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'suspended', 'closed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wallet_accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES app_users(id) ON DELETE RESTRICT,
    currency CHAR(3) NOT NULL CHECK (currency IN ('SAR', 'USD', 'AED', 'YER')),
    balance NUMERIC(24, 6) NOT NULL DEFAULT 0 CHECK (balance >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'demo'
        CHECK (status IN ('demo', 'pending_provider', 'active', 'frozen')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, currency)
);

CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    actor_user_id BIGINT REFERENCES app_users(id) ON DELETE RESTRICT,
    event_type VARCHAR(80) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_events_actor_created
    ON audit_events(actor_user_id, created_at DESC);
