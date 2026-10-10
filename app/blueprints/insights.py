from flask import Blueprint, jsonify

from app.blueprints.members import member_row
from app.extensions import get_db
from app.utils import fail, role_required

insights_bp = Blueprint("insights", __name__)


@insights_bp.get("/dashboard")
@role_required("admin", "trainer")
def dashboard():
    db = get_db()
    members = db.execute("SELECT COUNT(*) c FROM members").fetchone()["c"]
    active = db.execute("SELECT COUNT(*) c FROM members WHERE membership_state = 'active'").fetchone()["c"]
    sessions = db.execute("SELECT COUNT(*) c FROM sessions").fetchone()["c"]
    progress_updates = db.execute("SELECT COUNT(*) c FROM progress_log").fetchone()["c"]
    return jsonify(counts={
        "members": members,
        "active_memberships": active,
        "sessions": sessions,
        "progress_updates": progress_updates,
    }), 200


@insights_bp.get("/members/<name>/overview")
def member_overview(name):
    db = get_db()
    member = member_row(db, name)
    if member is None:
        return fail("member not found", 404)
    sessions = db.execute("SELECT COUNT(*) c FROM sessions WHERE member_name = ?", (name,)).fetchone()["c"]
    progress = db.execute("SELECT COUNT(*) c FROM progress_log WHERE member_name = ?", (name,)).fetchone()["c"]
    measurements = db.execute("SELECT COUNT(*) c FROM measurements WHERE member_name = ?", (name,)).fetchone()["c"]
    targets = db.execute("SELECT COUNT(*) c FROM targets WHERE member_name = ?", (name,)).fetchone()["c"]
    return jsonify(member=dict(member), counts={
        "sessions": sessions,
        "progress": progress,
        "measurements": measurements,
        "targets": targets,
    }), 200


@insights_bp.get("/analytics/summary")
@role_required("admin", "trainer")
def analytics_summary():
    db = get_db()
    total_members = db.execute("SELECT COUNT(*) c FROM members").fetchone()["c"]
    active = db.execute("SELECT COUNT(*) c FROM members WHERE membership_state = 'active'").fetchone()["c"]
    suspended = db.execute("SELECT COUNT(*) c FROM members WHERE membership_state = 'suspended'").fetchone()["c"]
    expired = db.execute("SELECT COUNT(*) c FROM members WHERE membership_state = 'expired'").fetchone()["c"]
    sessions = db.execute("SELECT COUNT(*) c FROM sessions").fetchone()["c"]
    avg_weight = db.execute("SELECT AVG(weight_kg) v FROM measurements WHERE weight_kg IS NOT NULL").fetchone()["v"]
    return jsonify(
        total_members=total_members,
        memberships={"active": active, "suspended": suspended, "expired": expired},
        total_sessions=sessions,
        average_measured_weight=round(avg_weight, 2) if avg_weight is not None else None,
    ), 200
