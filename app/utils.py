import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from functools import wraps

from flask import jsonify, session

PLAN_LIBRARY = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
}

ACTIVITY_FACTORS = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fail(message: str, status: int):
    return jsonify(error=message), status


def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("role") not in roles:
                return fail("an allowed role must be logged in", 403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def compute_bmi(weight_kg: float, height_m: float) -> float:
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("weight_kg and height_m must be > 0")
    return round(weight_kg / (height_m ** 2), 2)


def bmi_label(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def daily_kcal(weight_kg: float, height_cm: float, age: int, gender: str, activity: str) -> int:
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        raise ValueError("weight, height and age must be positive")
    gender = gender.lower()
    if gender not in {"male", "female"}:
        raise ValueError("gender must be male or female")
    if activity not in ACTIVITY_FACTORS:
        raise ValueError("activity must be sedentary, light, moderate or active")
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + (5 if gender == "male" else -161)
    return int(round(bmr * ACTIVITY_FACTORS[activity]))


def progress_svg(rows):
    width, height, margin = 700, 360, 50
    values = [float(r["weight_kg"]) for r in rows if r["weight_kg"] is not None]
    labels = [str(r["logged_at"])[:10] for r in rows if r["weight_kg"] is not None]
    root = ET.Element("svg", width=str(width), height=str(height), xmlns="http://www.w3.org/2000/svg")
    ET.SubElement(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="white")
    ET.SubElement(root, "text", x="30", y="25").text = "ACEest Progress Chart - Weight (kg)"
    if not values:
        ET.SubElement(root, "text", x="50", y="180").text = "No progress data"
        return ET.tostring(root, encoding="unicode")
    ymin, ymax = min(values), max(values)
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    plot_w, plot_h = width - 2 * margin, height - 2 * margin
    points = []
    for i, value in enumerate(values):
        x = margin if len(values) == 1 else margin + (plot_w * i / (len(values) - 1))
        y = margin + plot_h * (ymax - value) / (ymax - ymin)
        points.append((x, y))
    ET.SubElement(
        root, "line", x1=str(margin), y1=str(height - margin),
        x2=str(width - margin), y2=str(height - margin), stroke="black",
    )
    ET.SubElement(root, "line", x1=str(margin), y1=str(margin), x2=str(margin), y2=str(height - margin), stroke="black")
    poly_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    ET.SubElement(
        root, "polyline", points=poly_points, fill="none", stroke="blue", **{"stroke-width": "2"},
    )
    for (x, y), label, value in zip(points, labels, values):
        ET.SubElement(root, "circle", cx=f"{x:.1f}", cy=f"{y:.1f}", r="4", fill="blue")
        ET.SubElement(root, "text", x=f"{x:.1f}", y=f"{y-8:.1f}", **{"text-anchor": "middle"}).text = str(value)
        ET.SubElement(root, "text", x=f"{x:.1f}", y=str(height - 20), **{"text-anchor": "middle"}).text = label
    return ET.tostring(root, encoding="unicode")
