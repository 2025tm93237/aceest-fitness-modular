import tempfile

from app import create_app


def test_health():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        app = create_app(f.name)
        app.config["TESTING"] = True
        assert app.test_client().get("/health").status_code == 200


def test_service_info(client):
    body = client.get("/").get_json()
    assert body["service"] == "ACEest Fitness & Gym API"
    assert body["status"] == "running"
