import sqlite3

from flask import Blueprint, jsonify, request

from app.extensions import get_db
from app.utils import fail, role_required

movements_bp = Blueprint("movements", __name__, url_prefix="/movements")


@movements_bp.get("")
def list_movements():
    rows = get_db().execute("SELECT * FROM movements ORDER BY title").fetchall()
    return jsonify([dict(r) for r in rows]), 200


@movements_bp.post("")
@role_required("admin", "trainer")
def add_movement():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return fail("title is required", 400)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO movements (title, muscle_group, equipment) VALUES (?, ?, ?)",
            (title, data.get("muscle_group"), data.get("equipment")),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return fail("movement already exists", 409)
    return jsonify(message="movement created"), 201
