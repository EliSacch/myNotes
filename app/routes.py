from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db, login_manager
from app.models import Note

notes_bp = Blueprint("notes", __name__)
auth_bp = Blueprint("auth", __name__)
health_bp = Blueprint("health", __name__)


@login_manager.user_loader
def load_user(user_id):
    return None

@health_bp.route("/health/db")
def health_db_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"db_status": "ok"}), 200
    except Exception as e:
        return jsonify({"db_status": "error", "detail": str(e)}), 500

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return render_template("form/register.html", title="Create your account", action="/register")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return render_template("form/login.html", title="Login to your account", action="/login")
    

@notes_bp.route("/")
def index():
    notes = db.session.scalars(db.select(Note)).all()
    data = [note.to_dict() for note in notes]
    return render_template("index.html", page_title="Dashboard", notes=data)


@notes_bp.route("/addNote", methods=["GET", "POST"])
def add_note():
    if request.method == "POST":
        new_note = Note(
            Title=request.form.get("title"),
            IsList=False,
            Content=[{"checked": False, "content": request.form.get("content")}],
        )
        db.session.add(new_note)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            error_msg = "There was an error submitting this request. Please, try again."
            return render_template(
                "addNote.html",
                page_title="Add new note",
                action="/addNote",
                message=error_msg,
            )
    return render_template("addNote.html", page_title="Add new note", action="/addNote")


@notes_bp.route("/addList", methods=["GET", "POST"])
def add_list():
    if request.method == "POST":
        new_note = Note(
            Title=request.form.get("title"),
            IsList=True,
            Content=[{"checked": False, "content": request.form.get("content")}],
        )
        db.session.add(new_note)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            error_msg = "There was an error submitting this request. Please, try again."
            return render_template(
                "addList.html",
                page_title="Add new list",
                action="/addList",
                message=error_msg,
            )
    return render_template("addList.html", page_title="Add new list", action="/addList")
