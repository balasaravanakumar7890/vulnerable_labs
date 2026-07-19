# Application Design

## 1. Application Overview

### Purpose

Community Hub is a member-discussion portal with a private direct-message feature. It reproduces the writeup's condition: a logged-in but unrelated member can open a captured message URL.

### Feature list

- Member sign-in and sign-out.
- Profile summary for the active member.
- Private inbox and sent-message lists.
- Direct-message composition between known members.
- Email-notification handoff record for each message.
- Message permalink using a UUID in `MailMessageKey`.

### User roles

There is one application role: **community member**. Alice, Bruno, and Casey are members. The distinction is relationship-based: only a message's sender and recipient should be allowed to read it. No administrator role is necessary for the reported vulnerability.

### Architecture

Browser requests are handled by Flask/Gunicorn (`web`), which persists users, messages, and notification records to PostgreSQL (`db`) over an internal Docker bridge network. Flask's signed session cookie carries the authenticated member identifier. No file storage, API token, queue, or external service is needed.

### Workflow

1. A member authenticates with username and password.
2. The sender selects a recipient and submits a subject/body.
3. The app validates input, creates a UUID-keyed message, and creates a notification-handoff record in the same transaction.
4. The recipient normally opens the message from their inbox link.
5. The vulnerable detail route instead authorizes only the session, then uses `MailMessageKey` to retrieve the message.

## 2. Vulnerability Design

The intentional defect is in `app/app.py`'s `inbox` detail branch. It validates that `MailMessageKey` is a UUID and retrieves `Message` by primary key, but does not require the current member to be the message sender or recipient. It therefore models a broken object-level authorization check rather than UUID prediction.

The code remains secure in the surrounding workflow: authentication is required; inbox/sent listings are relationship-scoped; compose validates all values; state-changing forms use CSRF protection; output is autoescaped; and sensitive response headers are set. In particular, `Referrer-Policy: no-referrer` avoids adding a separate token-leak vulnerability. The captured URL represents the writeup's social-engineering or third-party-leak prerequisite.

## 3. Application Features

### Pages and forms

| Page | Route | Access | Form / purpose |
| --- | --- | --- | --- |
| Sign in | `GET /login` | Public | Username/password with CSRF token |
| Profile | `GET /network/members/profile/myaccount` | Member | Shows own profile only |
| Inbox | `GET /network/members/profile/myaccount/inbox` | Member | Lists recipient's messages |
| Message detail | `GET /network/members/profile/myaccount/inbox?MailMessageKey=<uuid>&IsFromInbox=True` | Member | Intentionally flawed object retrieval |
| Sent | `GET /network/members/profile/myaccount/sent` | Member | Lists sender's messages |
| Compose | `GET/POST /network/members/profile/myaccount/messages/compose` | Member | Recipient, subject, body, CSRF token |
| Sign out | `POST /logout` | Member | CSRF-protected sign-out |

`GET /` redirects to the inbox for authenticated members and to sign-in otherwise. There are no JSON APIs: every required interaction is a server-rendered HTTP endpoint.

### Permissions

| Action | Required permission | Enforcement |
| --- | --- | --- |
| Sign in | Valid account password | Password hash verification |
| View own profile | Authenticated member | Session ID lookup |
| List inbox | Message recipient | `recipient_id == current_user.id` |
| List sent | Message sender | `sender_id == current_user.id` |
| Send a message | Authenticated member | CSRF, recipient validation, DB constraints |
| View message detail | Sender or recipient | **Missing intentionally** |
| Sign out | Authenticated member | CSRF token |

## 4. Database Design

The complete executable DDL is in `database/init.sql`.

| Table | Purpose | Key relationships |
| --- | --- | --- |
| `users` | Member identity, email, password hash, creation time | Referenced by messages and notifications |
| `messages` | UUID-keyed direct-message content and metadata | `sender_id -> users.id`; `recipient_id -> users.id`; sender cannot equal recipient |
| `email_notifications` | One persisted notification handoff per message | `message_id -> messages.id` (unique); `recipient_id -> users.id` |

`messages_recipient_created_idx` and `messages_sender_created_idx` support the inbox and sent-list queries. Foreign keys use restrictive deletes so a member cannot be removed while it would orphan private communications.

## 5. Project Structure

```text
community-inbox-lab/
├── app/
│   ├── app.py                 routes, models, authentication, validation
│   ├── bootstrap.py           idempotent demo seed
│   ├── static/app.css         interface styling
│   └── templates/             server-rendered pages
├── database/init.sql          PostgreSQL schema
├── docs/                      design, instructor, security, development notes
├── docker-compose.yml         services, network, volume, configuration
├── Dockerfile                 non-root web image
├── requirements.txt           pinned Python dependencies
└── README.md                  setup and operating guide
```

## 6. Docker Setup

`docker-compose.yml` defines two services on `community-network`:

- `db`: PostgreSQL 16 with a named `postgres_data` volume and read-only initialization SQL mount.
- `web`: Python 3.12 slim image, running as an unprivileged `appuser`, waiting for the database health check, seeding the demo data, then serving Gunicorn on port 8080.

Environment variables are `DATABASE_URL`, `FLASK_SECRET_KEY`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`. Defaults allow `docker compose up --build` with no additional setup; `.env.example` provides a copyable configuration file. The only published service port is `8080:8080`; PostgreSQL stays inside the Compose network.
