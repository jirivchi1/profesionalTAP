from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models  # noqa: F401 — registers user_loader

    from app.controllers.public import public
    app.register_blueprint(public)

    from app.controllers.auth import auth
    app.register_blueprint(auth)

    from app.controllers.dashboard import dashboard
    app.register_blueprint(dashboard)

    from app.controllers.landing import landing
    app.register_blueprint(landing)

    from app.controllers.admin import admin
    app.register_blueprint(admin)

    return app
