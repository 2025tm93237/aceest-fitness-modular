from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from app.extensions import get_db
from app.utils import fail

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username, password = data.get("username"), data.get("password")
    if not username or not password:
        return fail("username and password are required", 400)
    db = get_db()
    row = db.execute(
        "SELECT username, password_hash, role FROM accounts WHERE username = ?", (username,)
    ).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        return fail("invalid credentials", 401)
    session.clear()
    session["username"] = row["username"]
    session["role"] = row["role"]
    return jsonify(username=row["username"], role=row["role"], message="login successful"), 200


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify(message="logout successful"), 200
