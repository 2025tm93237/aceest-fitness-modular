from flask import Blueprint, jsonify, request

from app.blueprints.members import member_row
from app.extensions import get_db
from app.utils import fail

targets_bp = Blueprint("targets", __name__, url_prefix="/members")


@targets_bp.post("/<name>/targets")
def add_target(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    data = request.get_json(silent=True) or {}
    if not data.get("target_type"):
        return fail("target_type is required", 400)
    db.execute(
        "INSERT INTO targets (member_name, target_type, target_value, due_date, state) VALUES (?, ?, ?, ?, 'active')",
        (name, data["target_type"], data.get("target_value"), data.get("due_date")),
    )
    db.commit()
    return jsonify(message="target created"), 201


@targets_bp.get("/<name>/targets")
def list_targets(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    rows = db.execute(
        "SELECT target_type, target_value, due_date, state FROM targets WHERE member_name = ? ORDER BY id DESC",
        (name,),
    ).fetchall()
    return jsonify([dict(r) for r in rows]), 200
