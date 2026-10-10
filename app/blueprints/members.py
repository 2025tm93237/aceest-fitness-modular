import sqlite3

from flask import Blueprint, jsonify, request

from app.extensions import get_db
from app.utils import fail, role_required, timestamp

members_bp = Blueprint("members", __name__, url_prefix="/members")


def member_row(db, name):
    return db.execute("SELECT * FROM members WHERE full_name = ?", (name,)).fetchone()


@members_bp.post("")
def create_member():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return fail("name is required", 400)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO members (full_name, age, gender, height_cm, weight_kg, target, membership_state, joined_at) "
            "VALUES (?, ?, ?, ?, ?, ?, 'active', ?)",
            (
                name, data.get("age"), data.get("gender"), data.get("height_cm"),
                data.get("weight_kg"), data.get("target"), timestamp(),
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return fail(f"member '{name}' already exists", 409)
    return jsonify(message=f"member '{name}' created"), 201


@members_bp.get("")
def list_members():
    rows = get_db().execute("SELECT * FROM members ORDER BY full_name").fetchall()
    return jsonify([dict(r) for r in rows]), 200


@members_bp.get("/<name>")
def get_member(name):
    row = member_row(get_db(), name)
    if row is None:
        return fail("member not found", 404)
    return jsonify(dict(row)), 200


@members_bp.delete("/<name>")
@role_required("admin", "trainer")
def delete_member(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    db.execute("DELETE FROM members WHERE full_name = ?", (name,))
    db.commit()
    return jsonify(message="member deleted"), 200
