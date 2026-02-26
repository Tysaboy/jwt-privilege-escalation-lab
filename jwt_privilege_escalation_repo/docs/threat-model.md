# Threat Model (Lab)

## Attacker capabilities
- Can register/login or obtain a legitimate user token.
- Can send requests with arbitrary Authorization headers.
- Does NOT have server source code in a real scenario (blackbox).

## Target security property
- Only admins should access `/admin`.

## Vulnerability
- HS256 relies on the secrecy and entropy of the signing secret.
- If the secret is weak/guessable, an attacker can forge a valid token with `role=admin`.

## Out of scope
- TLS / MITM threats
- Database injection
- Session fixation / CSRF (this lab uses Bearer tokens)
