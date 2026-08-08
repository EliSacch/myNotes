from flask import Blueprint, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Note

notes_bp = Blueprint("notes", __name__)


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
