#!/usr/bin/env python3
from flask import Flask, request, jsonify, abort
import sqlite3
import time
import os
import jwt
from functools import wraps

app = Flask(__name__)

JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_ME_TO_RANDOM_LONG_SECRET")
JWT_ISSUER = "local-lab-app"
JWT_EXP_SECONDS = 15 * 60  # 15 minutes

def init_db():
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    c.execute("DELETE FROM users")
    c.execute("INSERT INTO users VALUES (1, 'admin', 'admin123', 'admin')")
    c.execute("INSERT INTO users VALUES (2, 'user', 'password', 'user')")
    conn.commit()
    conn.close()

init_db()

def db_get_user(username: str):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    row = c.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row

def issue_token(user_id: int, username: str, role: str) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iss": JWT_ISSUER,
        "iat": now,
        "exp": now + JWT_EXP_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def require_auth(required_role: str | None = None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                abort(401)
            token = auth.removeprefix("Bearer ").strip()

            try:
                claims = jwt.decode(
                    token,
                    JWT_SECRET,
                    algorithms=["HS256"],
                    issuer=JWT_ISSUER,
                    options={"require": ["exp", "iat", "iss"]},
                )
            except jwt.PyJWTError:
                abort(401)

            if required_role is not None and claims.get("role") != required_role:
                abort(403)

            request.claims = claims
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.get("/")
def home():
    return "Try POST /api/login then GET /api/me and GET /admin"

@app.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "")

    user = db_get_user(username)
    if not user:
        abort(401)

    user_id, uname, pw, role = user
    if password != pw:
        abort(401)

    token = issue_token(user_id, uname, role)
    return jsonify({"token": token})

@app.get("/api/me")
@require_auth()
def api_me():
    return jsonify({"claims": request.claims})

@app.get("/admin")
@require_auth(required_role="admin")
def admin():
    return "Admin panel: only admin should see this."

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)
