from datetime import date

from flask import Blueprint, jsonify, make_response, request

from app.blueprints.members import member_row
from app.extensions import get_db
from app.utils import fail, progress_svg

progress_bp = Blueprint("progress", __name__, url_prefix="/members")


@progress_bp.post("/<name>/progress")
def add_progress(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    data = request.get_json(silent=True) or {}
    weight = data.get("weight_kg")
    if weight is None or float(weight) <= 0:
        return fail("positive weight_kg is required", 400)
    db.execute(
        "INSERT INTO progress_log (member_name, logged_at, weight_kg, remark) VALUES (?, ?, ?, ?)",
        (name, data.get("logged_at", date.today().isoformat()), weight, data.get("remark", "")),
    )
    db.commit()
    return jsonify(message="progress recorded"), 201


@progress_bp.get("/<name>/progress")
def list_progress(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    rows = db.execute(
        "SELECT logged_at, weight_kg, remark FROM progress_log WHERE member_name = ? ORDER BY logged_at",
        (name,),
    ).fetchall()
    return jsonify([dict(r) for r in rows]), 200


@progress_bp.get("/<name>/progress/chart")
def progress_chart(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    rows = db.execute(
        "SELECT logged_at, weight_kg FROM progress_log WHERE member_name = ? ORDER BY logged_at",
        (name,),
    ).fetchall()
    response = make_response(progress_svg(rows))
    response.headers["Content-Type"] = "image/svg+xml"
    return response
