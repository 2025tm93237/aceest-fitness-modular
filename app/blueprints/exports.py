import csv
import io

from flask import Blueprint, make_response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.blueprints.members import member_row
from app.extensions import get_db
from app.utils import fail

exports_bp = Blueprint("exports", __name__, url_prefix="/members")


@exports_bp.get("/<name>/export.csv")
def export_csv(name):
    db = get_db()
    if member_row(db, name) is None:
        return fail("member not found", 404)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "movement", "minutes", "kcal_burned", "remarks"])
    rows = db.execute(
        "SELECT session_date, movement_title, minutes, kcal_burned, remarks FROM sessions "
        "WHERE member_name = ? ORDER BY session_date",
        (name,),
    ).fetchall()
    for row in rows:
        writer.writerow(list(row))
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f'attachment; filename="{name}_sessions.csv"'
    return response


@exports_bp.get("/<name>/report.pdf")
def report_pdf(name):
    db = get_db()
    member = member_row(db, name)
    if member is None:
        return fail("member not found", 404)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"ACEest Report - {name}")
    y = 800
    pdf.drawString(50, y, "ACEest Fitness & Gym - Member Report")
    y -= 25
    pdf.drawString(50, y, f"Member: {name}")
    y -= 18
    pdf.drawString(50, y, f"Membership: {member['membership_state']}")
    y -= 18
    pdf.drawString(50, y, f"Target: {member['target'] or 'Not set'}")
    y -= 30
    pdf.drawString(50, y, "Recent Progress")
    for row in db.execute(
        "SELECT logged_at, weight_kg FROM progress_log WHERE member_name = ? ORDER BY logged_at DESC LIMIT 8",
        (name,),
    ).fetchall():
        y -= 16
        pdf.drawString(60, y, f"{row['logged_at']}: {row['weight_kg']} kg")
    y -= 20
    pdf.drawString(50, y, "Recent Sessions")
    for row in db.execute(
        "SELECT session_date, movement_title, minutes FROM sessions "
        "WHERE member_name = ? ORDER BY session_date DESC LIMIT 8",
        (name,),
    ).fetchall():
        y -= 16
        label = f"{row['session_date']}: {row['movement_title']} - {row['minutes']} min"
        pdf.drawString(60, y, label)
        if y < 80:
            pdf.showPage()
            y = 800
    pdf.save()
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="{name}_report.pdf"'
    return response
