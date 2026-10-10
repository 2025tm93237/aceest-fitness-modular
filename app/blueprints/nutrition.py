from flask import Blueprint, jsonify, request

from app.extensions import get_db
from app.utils import daily_kcal, fail

nutrition_bp = Blueprint("nutrition", __name__, url_prefix="/members")


@nutrition_bp.get("/<name>/calories")
def calories(name):
    row = get_db().execute(
        "SELECT age, gender, height_cm, weight_kg FROM members WHERE full_name = ?", (name,)
    ).fetchone()
    if row is None:
        return fail("member not found", 404)
    activity = request.args.get("activity", "moderate")
    try:
        value = daily_kcal(
            float(row["weight_kg"]), float(row["height_cm"]), int(row["age"]), row["gender"], activity,
        )
    except (TypeError, ValueError):
        return fail("member age, gender, height_cm, weight_kg and activity must all be valid", 400)
    return jsonify(name=name, daily_calories=value), 200
