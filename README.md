# Vulnerable Labs

Each lab is a minimal but realistic application that reproduces a single vulnerability while keeping every unrelated feature secure. 

---

---

## Learning Workflow

For every lab, follow the same process:

```text
1. Start the lab
        ↓
2. Map the application
        ↓
3. Enumerate endpoints and roles
        ↓
4. Build a threat model
        ↓
5. Test manually
        ↓
6. Discover the vulnerability
        ↓
7. Develop an exploit
        ↓
8. Read the source code
        ↓
9. Identify the root cause
        ↓
10. Patch the vulnerability
        ↓
11. Verify the fix
        ↓
12. Document findings
```

---

---

# What Each Lab Contains

Every lab includes:

- Vulnerable application
- Docker configuration
- Database initialization
- Source code
- Test accounts
- Exploit guide
- Root cause analysis
- Secure implementation
- Patch instructions

Typical structure:

```
lab-name/

├── app/
├── database/
├── docker/
├── docs/
│
├── docker-compose.yml
├── Dockerfile
├── README.md
├── solution.md
└── writeup.md
```

---

# Technologies

Depending on the lab, technologies may include:

- Python (Flask)
- PHP
- Node.js
- Express
- MySQL
- SQLite
- Docker
- Docker Compose
- HTML
- JavaScript

The technology stack is chosen based on what best represents the original vulnerability.

---

# Running a Lab

Navigate to a lab directory.

```bash
cd idor/memshare-lab
```

Build and start the containers.

```bash
docker compose up --build
```

Stop the lab.

```bash
docker compose down
```

Reset the environment.

```bash
docker compose down -v
docker compose up --build
```

---


---

# Learning Resources Used

Labs are inspired by publicly available educational material, including:

- PortSwigger Web Security Academy
- Public bug bounty writeups
- Public HackerOne disclosures
- Public Bugcrowd reports
- Public CVEs
- OWASP documentation

No proprietary code or private reports are included.

---

# Intended Audience

This repository is intended for:

- Bug bounty hunters
- Penetration testers
- Security engineers
- Students
- CTF players transitioning to real-world testing
- Developers learning secure coding

---

# Disclaimer

These applications are intentionally vulnerable and are designed **only** for educational purposes.

Run them only in an isolated local environment.

Do not deploy them to public infrastructure.

Do not use these techniques against systems without explicit authorization.

---


# License

This project is released for educational purposes. Refer to the repository license for usage terms.
