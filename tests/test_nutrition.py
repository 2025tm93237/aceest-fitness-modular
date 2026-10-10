import pytest

from app.utils import bmi_label, compute_bmi, daily_kcal
from helpers import register_member


def test_bmi_helpers():
    assert compute_bmi(60, 1.6) == 23.44
    assert bmi_label(18.4) == "Underweight"
    assert bmi_label(24.9) == "Normal"
    assert bmi_label(29.9) == "Overweight"
    assert bmi_label(30) == "Obese"


def test_bmi_validation_and_calories(client):
    register_member(client, height_cm=160, weight_kg=60)
    assert client.get("/members/Ravi/calories?activity=moderate").status_code == 200
    assert client.get("/members/Ravi/calories?activity=bad").status_code == 400
    with pytest.raises(ValueError):
        daily_kcal(60, 160, 30, "x", "moderate")
