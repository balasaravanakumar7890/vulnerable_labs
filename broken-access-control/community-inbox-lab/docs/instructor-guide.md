# Instructor Guide

## Learning objectives

- Distinguish authentication from object-level authorization.
- Recognize a UUID in a URL as an identifier, not proof of permission.
- Test a captured authenticated link under a different authenticated session.
- Explain why opaque identifiers and email notification URLs do not replace an authorization check.

## Normal member flow

1. Alice signs in and sends Bruno a direct message using **New message**.
2. The application creates a message row and a notification-handoff row for Bruno.
3. Bruno signs in, sees only messages where he is the recipient, and opens one from his inbox.
4. Alice sees only messages where she is the sender on the Sent page.

The inbox and sent list queries are correctly scoped to the logged-in member. The application also requires an authenticated session before the detail route is reached.

## Expected attack path

1. Log in as `bruno` with `DemoPass!23` and open **Q3 partner renewal notes**.
2. Copy the complete address, including `MailMessageKey`.
3. Log out, then log in as `casey` in a different browser profile (or use a private window).
4. Visit the copied address unchanged.
5. Observe the message content, sender, and recipient even though Casey is unrelated to it.

Use the seeded key if a second session is inconvenient:

```text
/network/members/profile/myaccount/inbox?MailMessageKey=2c1139f1-c131-4db4-b2f1-ea5168064b4e&IsFromInbox=True
```

## Vulnerable flow

The detail branch of `GET /network/members/profile/myaccount/inbox` parses the `MailMessageKey`, looks up a message by that key, and renders it. It requires a valid login, but it fails to assert `current_user.id == message.sender_id` or `current_user.id == message.recipient_id`.

`IsFromInbox` mirrors the original URL shape but is not an authorization control. The UUID has high entropy, but a member who captures it through a forwarded notification, social engineering, logs, or another leakage path can reuse it.

## Expected exploit result

Casey receives HTTP 200 and the full direct-message content. An unknown or malformed key receives 404. A logged-out visitor is redirected to sign in. These distinctions help students identify the precise authorization failure rather than a public exposure.

## Hints

- Compare the list route and the detail route's database queries.
- Test with two authenticated identities, not only logged-in versus logged-out.
- Keep every query parameter while replaying the URL.
- UUIDs make guessing difficult; they do not make access authorized.

## Common mistakes

- Treating a copied message link as a passwordless login link. It still needs an authenticated Community Hub account.
- Calling this only an information leak. The primary defect is missing object-level authorization.
- Assuming the recipient list proves the detail endpoint is protected.
- Testing only URL mutation. The scenario is capability reuse after token disclosure, not UUID enumeration.

## Suggested remediation discussion

Require a participant check at the message lookup boundary and return 404 or 403 for non-participants. Avoid sending reusable object identifiers in URLs where possible; protect notification links with short-lived, purpose-bound tokens if a direct-link workflow is required. Maintain restrictive referrer policies and avoid third-party resources on sensitive pages.
