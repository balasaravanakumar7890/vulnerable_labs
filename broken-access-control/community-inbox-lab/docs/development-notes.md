# Development Notes

## Why each component exists

- **Login and three seeded members:** the exercise requires a sender, recipient, and unrelated authenticated attacker.
- **Inbox, sent, compose, and message-detail pages:** these are the smallest realistic private-messaging workflow that produces and replays a message URL.
- **`messages` table:** holds the protected conversation and uses a UUID message key, matching the writeup.
- **`email_notifications` table:** records the notification handoff implied by the writeup without needing a real email provider or a background queue.
- **PostgreSQL:** supplies a realistic relational authorization boundary and verifies schema relationships.
- **Docker Compose:** provides one-command, repeatable startup and a resettable database state.

## Deliberate exclusions

There is no registration, password reset, attachment handling, member search, public discussion feed, administrator role, REST API, external SMTP provider, third-party analytics, or worker queue. None is required to demonstrate that a copied message key is accepted under another member's session. Excluding them keeps the attack surface and instructional focus narrow.

## Workflow and storage decisions

Sending a message is synchronous: it validates input, writes the message, creates one notification-handoff record, and redirects to Sent. No files are accepted or stored. Authentication uses Flask's signed server-side-session cookie; no bearer tokens are exposed to browser scripts. Message UUIDs are stored as PostgreSQL UUID values and appear only in detail links.

## Configuration decisions

`.env.example` contains local-only development defaults. Docker Compose supplies safe defaults so `docker compose up --build` works without copying it. Change `FLASK_SECRET_KEY` before sharing the stack with others. HTTPS is intentionally not bundled for a localhost lab; use a TLS-terminating reverse proxy and set `SESSION_COOKIE_SECURE=True` for any non-local deployment.
