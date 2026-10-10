def register_member(c, name="Ravi", **kwargs):
    payload = {
        "name": name,
        "age": 28,
        "gender": "male",
        "height_cm": 175,
        "weight_kg": 78,
        "target": "Muscle Gain",
    }
    payload.update(kwargs)
    return c.post("/members", json=payload)


def login_as(c, role):
    creds = {"admin": ("admin", "admin123"), "trainer": ("trainer", "trainer123")}
    username, password = creds[role]
    return c.post("/login", json={"username": username, "password": password})
