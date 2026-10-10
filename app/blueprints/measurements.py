from datetime import date

from flask import Blueprint, jsonify, request

from app.blueprints.members import member_row
from app.extensions import get_db
from app.utils import fail

measurements_bp = Blueprint("measurements", __name__, url_prefix="/members")


@measurements_bp.post("/<name>/measurements")
def add_measurement(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    data = request.get_json(silent=True) or {}
    db.execute(
        "INSERT INTO measurements "
        "(member_name, logged_at, weight_kg, body_fat_pct, chest_cm, waist_cm, hip_cm, remarks) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            name,
            data.get("logged_at", date.today().isoformat()),
            data.get("weight_kg"),
            data.get("body_fat_pct"),
            data.get("chest_cm"),
            data.get("waist_cm"),
            data.get("hip_cm"),
            data.get("remarks", ""),
        ),
    )
    db.commit()
    return jsonify(message="measurement recorded"), 201


@measurements_bp.get("/<name>/measurements")
def list_measurements(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    rows = db.execute(
        "SELECT logged_at, weight_kg, body_fat_pct, chest_cm, waist_cm, hip_cm, remarks FROM measurements "
        "WHERE member_name = ? ORDER BY logged_at DESC",
        (name,),
    ).fetchall()
    return jsonify([dict(r) for r in rows]), 200
