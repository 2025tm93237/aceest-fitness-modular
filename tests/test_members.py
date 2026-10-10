from helpers import login_as, register_member


def test_member_create(client):
    assert register_member(client).status_code == 201


def test_member_list_and_get(client):
    register_member(client)
    assert len(client.get("/members").get_json()) == 1
    assert client.get("/members/Ravi").get_json()["full_name"] == "Ravi"


def test_duplicate_member(client):
    register_member(client)
    assert register_member(client).status_code == 409


def test_member_not_found(client):
    assert client.get("/members/Nobody").status_code == 404


def test_protected_delete_requires_role(client):
    register_member(client)
    assert client.delete("/members/Ravi").status_code == 403


def test_member_delete(client):
    register_member(client)
    login_as(client, "admin")
    assert client.delete("/members/Ravi").status_code == 200
    assert client.get("/members/Ravi").status_code == 404
