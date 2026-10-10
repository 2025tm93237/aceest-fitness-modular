import os
from typing import Optional

from flask import Flask

from app.extensions import close_db
from app.models import init_db


def create_app(db_path: Optional[str] = None) -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "aceest_fitness.db")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-key")

    app.teardown_appcontext(close_db)

    from app.blueprints.core import core_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.members import members_bp
    from app.blueprints.plans import plans_bp
    from app.blueprints.nutrition import nutrition_bp

    for bp in (
        core_bp, auth_bp, members_bp, plans_bp,
        nutrition_bp,
    ):
        app.register_blueprint(bp)

    init_db(app.config["DB_PATH"])
    return app
