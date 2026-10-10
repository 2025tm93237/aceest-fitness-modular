from flask import Blueprint, jsonify, request

from app.blueprints.members import member_row
from app.extensions import get_db
from app.utils import PLAN_LIBRARY, fail, timestamp

plans_bp = Blueprint("plans", __name__, url_prefix="/members")


@plans_bp.post("/<name>/plan")
def generate_plan(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    data = request.get_json(silent=True) or {}
    plan_type = data.get("plan_type") or "Beginner"
    if plan_type not in PLAN_LIBRARY:
        return fail(f"unknown plan_type '{plan_type}'", 400)
    blueprint_text = PLAN_LIBRARY[plan_type][0]
    db.execute(
        "INSERT INTO training_plans (member_name, plan_type, blueprint_text, generated_at) VALUES (?, ?, ?, ?)",
        (name, plan_type, blueprint_text, timestamp()),
    )
    db.commit()
    return jsonify(name=name, plan_type=plan_type, plan=blueprint_text), 201


@plans_bp.get("/<name>/plans")
def list_plans(name):
    db = get_db()
    rows = db.execute(
        "SELECT plan_type, blueprint_text, generated_at FROM training_plans WHERE member_name = ? ORDER BY id DESC",
        (name,),
    ).fetchall()
    if not rows and member_row(db, name) is None:
        return fail("member not found", 404)
    return jsonify([dict(r) for r in rows]), 200
