# Community Hub: Broken Access Control Lab

Community Hub is a Dockerized training lab for a message-detail authorization failure. It is intentionally small: members can sign in, send direct messages, view their own inbox and sent mail, and open message links. The supplied writeup is modeled by a single flawed detail route that accepts a message UUID from the URL without checking that the active member is a participant.

This lab is based on the following public resources:

- [Broken access control vulnerability in hp product](https://medium.com/@cyberweapons/a-story-of-a-700-broken-access-control-2ec2c21f6ffe?sharedUserId=pbalasaravanakumar)

## Architecture

The `web` service is a Flask application served by Gunicorn. The `db` service is PostgreSQL 16 with a persistent named volume. On its first start, the web service seeds three demo members and one message. Docker's database health check prevents the application from starting before PostgreSQL is ready.

There is no external mail provider, file storage, API token, or background worker. The `email_notifications` table represents the application's persisted notification handoff; a copied notification link is the realistic prerequisite for the exercise without adding unrelated infrastructure.

## Requirements

- Docker Engine with Docker Compose v2
- Port `8080` available locally

## Install and run

```bash
cd broken-access-control/community-inbox-lab
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8080`. Use `docker compose up -d --build` to run in the background and `docker compose logs -f web` to inspect application logs.

## Demo members

All demo accounts use `DemoPass!23`:

| Purpose | Username | Email |
| --- | --- | --- |
| Sender | `alice` | `alice@example.test` |
| Recipient | `bruno` | `bruno@example.test` |
| Attacker | `casey` | `casey@example.test` |

The seeded Alice-to-Bruno message has the key `2c1139f1-c131-4db4-b2f1-ea5168064b4e`.

## Testing the lab

1. Sign in as `bruno`, open the first inbox message, and copy its full URL.
2. Sign out and sign in as `casey` in a separate browser profile or private window.
3. Paste the copied URL. Casey can view Alice and Bruno's private message despite not being a sender or recipient.

For the exact route shape from the writeup, use:

```text
http://localhost:8080/network/members/profile/myaccount/inbox?MailMessageKey=2c1139f1-c131-4db4-b2f1-ea5168064b4e&IsFromInbox=True
```

The app deliberately has no JSON API because a server-rendered inbox is sufficient to reproduce the issue. See `docs/instructor-guide.md` for guided exercises and `docs/security.md` for scope and threat model.

## Reset the database

```bash
docker compose down -v
docker compose up --build
```

`down -v` removes only the lab's named PostgreSQL volume and restores the seeded state on the next startup.

## Folder structure

```text
.
├── app/                 Flask application, templates, and styles
├── database/init.sql    PostgreSQL schema and indexes
├── docs/                Instructor, security, and development notes
├── docker-compose.yml   Web and database services
├── Dockerfile           Non-root application image
└── .env.example         Local configuration template
```

## Troubleshooting

- **Port conflict:** change `8080:8080` in `docker-compose.yml` to an unused host port.
- **Old seed data:** run `docker compose down -v` before bringing the stack up again.
- **Database connection failure:** wait for `db` to become healthy with `docker compose ps`, then inspect `docker compose logs db`.
- **Login fails:** use the case-sensitive password `DemoPass!23`; usernames are lowercase.

## Safety

Run this lab only on a local, isolated training environment. The authorization flaw is intentional and must never be used as an application pattern.
