from flask import Blueprint, jsonify

core_bp = Blueprint("core", __name__)


@core_bp.get("/")
def service_info():
    return jsonify(service="ACEest Fitness & Gym API", status="running", version="modular-1.1")


@core_bp.get("/health")
def health():
    return jsonify(status="ok"), 200
