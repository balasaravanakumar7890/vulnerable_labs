# Security Documentation

## Intentional vulnerability

`app/app.py` intentionally omits the object-level participant check in the message-detail branch of `GET /network/members/profile/myaccount/inbox`. Any authenticated Community Hub member holding a valid `MailMessageKey` can read that message.

This is broken access control (CWE-862 / CWE-639). The key is a UUID to reflect the writeup's opaque message token, but it is used only as a locator. It is not a grant of access.

## Secure implementations elsewhere

- Passwords use Werkzeug's adaptive password hashing helpers; no passwords are logged or seeded in plaintext.
- Login clears the prior session before establishing an authenticated session.
- Session cookies are `HttpOnly` and `SameSite=Lax`; production deployments should additionally enable `Secure` behind HTTPS.
- Every state-changing form has a per-session CSRF token verified with constant-time comparison.
- Compose validates recipients, rejects self-delivery, bounds subject/body lengths, and uses SQLAlchemy parameter binding.
- Inbox and sent list queries are scoped to the active member.
- Jinja autoescaping renders message content safely; the template does not mark user content safe.
- Response headers include CSP, no-referrer policy, anti-framing, nosniff, and no-store directives.
- PostgreSQL constraints and foreign keys enforce message integrity.

## Threat model

An attacker is an ordinary authenticated member. They can obtain another member's message URL through a forwarded notification, social engineering, browser history, logs, or a third-party referrer leak outside this minimal lab. They cannot guess UUIDs at practical scale and do not need administrator access. The protected asset is the confidentiality of direct-message metadata and content.

The lab deliberately scopes the defect to authorization after a key is obtained. Its `Referrer-Policy: no-referrer` header prevents the application itself from adding a second, unrelated URL-leakage defect. In a real assessment, investigate external notification content, third-party resources, analytics, redirects, and referrer handling as potential token sources.

## Why this lab exists

Teams often add a login check and believe UUID-based URLs are private. This lab shows why object ownership must be checked at every sensitive object retrieval, independent of how hard its identifier is to predict.

## Repair sketch

The vulnerable lookup needs a participant predicate, conceptually:

```python
message = db.session.scalar(
    db.select(Message).where(
        Message.id == key,
        (Message.sender_id == user.id) | (Message.recipient_id == user.id),
    )
)
```

This code is documentation only; do not apply it if you want the exercise to remain vulnerable.
