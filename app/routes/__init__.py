from flask import jsonify
from sqlalchemy import text
from app.extensions import db
from flask import Blueprint

health_bp = Blueprint("health", __name__)

@health_bp.route("/health/db")
def health_db_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"db_status": "ok"}), 200
    except Exception as e:
        return jsonify({"db_status": "error", "detail": str(e)}), 500

from app.routes.auth import auth_bp
from app.routes.notes import notes_bp

__all__ = ["health_bp", "auth_bp", "notes_bp"] 