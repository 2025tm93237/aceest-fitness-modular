import os
import tempfile

import pytest

from app import create_app


@pytest.fixture
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    app = create_app(path)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    os.unlink(path)
