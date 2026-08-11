import os

from flask import Flask

from app.extensions import db, migrate, login_manager


def create_app():
    app = Flask(
        __name__,
        template_folder="./templates",
        static_folder="../static",
        
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    migrate.init_app(app, db)

    from app import models  # noqa: F401
    from app.routes import health_bp, auth_bp, index_bp, dashboards_bp, notes_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(notes_bp)

    return app
