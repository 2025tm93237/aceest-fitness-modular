from flask import Blueprint, jsonify, request

from app.blueprints.members import member_row
from app.extensions import get_db
from app.utils import fail, role_required

membership_bp = Blueprint("membership", __name__, url_prefix="/members")

VALID_STATES = {"active", "suspended", "expired"}


@membership_bp.get("/<name>/membership")
def read_membership(name):
    row = member_row(get_db(), name)
    if row is None:
        return fail("member not found", 404)
    return jsonify(name=name, membership_state=row["membership_state"]), 200


@membership_bp.patch("/<name>/membership")
@role_required("admin", "trainer")
def update_membership(name):
    data = request.get_json(silent=True) or {}
    state = (data.get("state") or "").lower()
    if state not in VALID_STATES:
        return fail("state must be active, suspended or expired", 400)
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    db.execute("UPDATE members SET membership_state = ? WHERE full_name = ?", (state, name))
    db.commit()
    return jsonify(name=name, membership_state=state), 200
