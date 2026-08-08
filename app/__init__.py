import os

from flask import Flask

from app.extensions import db, migrate


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401
    from app.routes import notes_bp

    app.register_blueprint(notes_bp)

    return app
