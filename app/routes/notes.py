import hmac
import re
import secrets

from flask import Blueprint, abort, redirect, render_template, request, session, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Note

notes_bp = Blueprint("notes", __name__)


def _notes_csrf_token():
    csrf_token = session.get("notes_csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["notes_csrf_token"] = csrf_token
    return csrf_token

def _has_valid_notes_csrf_token():
    submitted_token = request.form.get("csrf_token", "")
    stored_token = session.get("notes_csrf_token", "")
    return (
        isinstance(submitted_token, str)
        and isinstance(stored_token, str)
        and hmac.compare_digest(submitted_token, stored_token)
    )

@notes_bp.route("/")
@login_required
def index():
    notes = db.session.scalars(db.select(Note)).all()
    data = [note.to_dict() for note in notes]
    return render_template("index.html", page_title="Dashboard", notes=data, csrf_token=_notes_csrf_token())


@notes_bp.route("/addNote", methods=["GET", "POST"])
@login_required
def add_note():
    if request.method == "POST":
        if not _has_valid_notes_csrf_token():
            abort(400, description="Invalid CSRF token.")

        new_note = Note(
            Title=request.form.get("title"),
            IsList=False,
            Content=[{"checked": False, "content": request.form.get("content")}],
        )
        db.session.add(new_note)
        try:
            db.session.commit()
            session.pop("notes_csrf_token", None)
        except SQLAlchemyError:
            db.session.rollback()
            flash("There was an error submitting this request. Please try again.", "error")
            return redirect(url_for("notes.index"))
        return redirect(url_for("notes.index"))
    return redirect(url_for("notes.index"))


@notes_bp.route("/editNote/<int:note_id>", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = db.session.get(Note, note_id)
    if not note:
        abort(404, description="Note not found.")
    if request.method == "POST":
        note.Title = request.form.get("title")
        note.Content = [{"checked": False, "content": request.form.get("content")}]
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("There was an error submitting this request. Please try again.", "error")
            return redirect(url_for("notes.index"))
        return redirect(url_for("notes.index"))
    return render_template("editNote.html", page_title="Edit note", note=note.to_dict(), csrf_token=_notes_csrf_token())

@notes_bp.route("/addList", methods=["GET", "POST"])
@login_required
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
