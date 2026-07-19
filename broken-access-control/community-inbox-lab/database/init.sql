CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(32) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_username_format CHECK (username ~ '^[a-z0-9][a-z0-9_-]{2,31}$')
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    sender_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    recipient_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    subject VARCHAR(120) NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT messages_no_self_delivery CHECK (sender_id <> recipient_id),
    CONSTRAINT messages_subject_not_blank CHECK (length(btrim(subject)) > 0),
    CONSTRAINT messages_body_not_blank CHECK (length(btrim(body)) > 0)
);

CREATE INDEX messages_recipient_created_idx ON messages (recipient_id, created_at DESC);
CREATE INDEX messages_sender_created_idx ON messages (sender_id, created_at DESC);

CREATE TABLE email_notifications (
    id BIGSERIAL PRIMARY KEY,
    message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE CASCADE,
    recipient_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    recipient_email VARCHAR(254) NOT NULL,
    delivered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
