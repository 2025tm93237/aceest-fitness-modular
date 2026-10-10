from datetime import date

from flask import Blueprint, jsonify, request

from app.blueprints.members import member_row
from app.extensions import get_db
from app.utils import fail

sessions_bp = Blueprint("sessions", __name__, url_prefix="/members")


@sessions_bp.post("/<name>/sessions")
def log_session(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    data = request.get_json(silent=True) or {}
    movement_title = data.get("movement_title", "General")
    if movement_title != "General" and db.execute(
        "SELECT title FROM movements WHERE title = ?", (movement_title,)
    ).fetchone() is None:
        return fail("movement not found", 404)
    db.execute(
        "INSERT INTO sessions (member_name, movement_title, session_date, minutes, kcal_burned, remarks) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            name,
            movement_title,
            data.get("session_date", date.today().isoformat()),
            data.get("minutes", 30),
            data.get("kcal_burned", 0),
            data.get("remarks", ""),
        ),
    )
    db.commit()
    return jsonify(message="session logged"), 201


@sessions_bp.get("/<name>/sessions")
def list_sessions(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    rows = db.execute(
        "SELECT movement_title, session_date, minutes, kcal_burned, remarks FROM sessions "
        "WHERE member_name = ? ORDER BY session_date DESC",
        (name,),
    ).fetchall()
    return jsonify([dict(r) for r in rows]), 200
