from helpers import register_member


def test_csv_export(client):
    register_member(client)
    response = client.get("/members/Ravi/export.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["Content-Type"]
    assert b"movement" in response.data
    assert client.get("/members/Nobody/export.csv").status_code == 404


def test_pdf_export(client):
    register_member(client)
    response = client.get("/members/Ravi/report.pdf")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/pdf")
    assert response.data.startswith(b"%PDF")
