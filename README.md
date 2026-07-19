# Vulnerable Labs

> A collection of intentionally vulnerable, Dockerized web applications built from real-world bug bounty reports, CVEs, PortSwigger labs, and public writeups.

The goal of this repository is to understand vulnerabilities from the inside out—not just exploit them.

Each lab is a minimal but realistic application that reproduces a single vulnerability while keeping every unrelated feature secure. This makes it easier to study the root cause, exploit methodology, source code, and remediation without unnecessary complexity.

---

## Objectives

- Learn how vulnerabilities actually occur in production applications.
- Practice reconnaissance and manual testing.
- Understand backend implementation and trust boundaries.
- Analyze vulnerable source code.
- Patch the vulnerability.
- Verify the fix by retesting.
- Build methodology that transfers to real bug bounty programs.

---

## Design Principles

Every lab follows these principles:

- One intentional vulnerability per lab.
- Only the required features are implemented.
- All unrelated functionality is implemented securely.
- Realistic workflows instead of toy examples.
- Fully Dockerized for one-command setup.
- Source code is included.
- Exploit documentation is provided.
- Remediation guidance is included.

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

# Repository Structure

```
vulnerable-labs/
│
├── idor/
│   ├── memshare-lab/
│   ├── document-sharing/
│   └── ...
│
├── sqli/
│
├── xss/
│
├── csrf/
│
├── ssrf/
│
├── auth/
│
├── business-logic/
│
├── mass-assignment/
│
├── api/
│
└── ...
```

Each vulnerability category contains one or more independent labs.

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

# Lab Methodology

Each lab is intended to be approached like a real bug bounty target.

Avoid reading the solution immediately.

Recommended approach:

- Explore the application
- Identify available functionality
- Enumerate endpoints
- Test authorization
- Analyze API behavior
- Attempt exploitation
- Read the source code
- Patch the issue
- Verify the fix

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

# Roadmap

- [ ] IDOR
- [ ] SQL Injection
- [ ] XSS
- [ ] CSRF
- [ ] SSRF
- [ ] Authentication flaws
- [ ] Authorization flaws
- [ ] Business Logic vulnerabilities
- [ ] API vulnerabilities
- [ ] File Upload
- [ ] Path Traversal
- [ ] Command Injection
- [ ] XXE
- [ ] Race Conditions
- [ ] JWT vulnerabilities
- [ ] OAuth vulnerabilities
- [ ] GraphQL vulnerabilities
- [ ] Prototype Pollution

---

# License

This project is released for educational purposes. Refer to the repository license for usage terms.
