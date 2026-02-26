# Workflow Notes — JWT Privilege Escalation (Local Lab)

## Setup
- Start app: `python3 src/app.py`
- Login endpoint: `POST /api/login`
- Auth header: `Authorization: Bearer <token>`

## Observations
- `GET /api/me` returns decoded claims
- `/admin` requires `role=admin` and returns 403 for normal user tokens

## Attack (Controlled Lab)
1. Obtain a normal user JWT via `/api/login`.
2. Decode header/payload to confirm `alg=HS256` and presence of `role` claim.
3. In the lab, demonstrate that a weak signing secret can be discovered (e.g., via a targeted wordlist).
4. Forge a new token with `role=admin` and verify `/admin` returns success.

## Fix Verification
- Run `src/secure_app.py` with a strong random `JWT_SECRET`.
- Confirm the same approach no longer works in practice (high entropy defeats guessing).
