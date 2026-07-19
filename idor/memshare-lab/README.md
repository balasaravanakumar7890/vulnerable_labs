# MemShare Security Lab: Insecure Direct Object Reference (IDOR)

This lab is based on the following public resources:

- [How I Found an Insecure Direct Object Reference in TikTok](https://medium.com/@mrhavit/how-i-found-an-insecure-direct-object-reference-in-tiktok-c7303addf223?sharedUserId=pbalasaravanakumar)

## Project Overview
MemShare is a minimal social media platform mimicking the core functionality of sharing "memories." This lab is designed to reproduce a real-world IDOR vulnerability discovered in a major social media platform's privacy modification functionality.

## Architecture
- **Backend:** Python (Flask)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose

## Requirements
- Docker
- Docker Compose

## Installation & Run Instructions
1. Run `docker compose up --build -d` in this directory.
2. Access the application at `http://localhost:5000`.

## Credentials (Demo Users)
- **Victim:** `victim_user` / `password123`
- **Attacker:** `attacker_user` / `password123`

## Testing Instructions
Interact with the application as a normal user. Use a proxy like Burp Suite to inspect the API traffic when changing a memory's privacy settings. Try to view the victim's private memory!

## Reset Database
To completely reset the lab environment:
`docker compose down -v`
`docker compose up -d`
