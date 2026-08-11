import hmac
import re
import secrets

from flask import Blueprint, abort, redirect, render_template, request, session, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Note

notes_bp = Blueprint("notes", __name__)
_NOTE_FORM_ERRORS_KEY = "note_form_errors"
_NOTE_FORM_VALUES_KEY = "note_form_values"


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


def _redirect_to_index_with_errors(form_key, errors, values=None):
    form_key = str(form_key)
    session[_NOTE_FORM_ERRORS_KEY] = {form_key: errors}
    if values is not None:
        session[_NOTE_FORM_VALUES_KEY] = {form_key: values}
    return redirect(url_for("dashboards.index"))


def _submitted_note_values():
    return {
        "title": request.form.get("title", ""),
        "content": request.form.get("content", ""),
    }

@notes_bp.route("/listNotes")
@login_required
def list_notes():
    notes = db.session.scalars(db.select(Note).where(Note.owner_id == current_user.id).order_by(Note.created_at.asc()))
    data = [note.to_dict() for note in notes]
    errors = session.pop(_NOTE_FORM_ERRORS_KEY, {})
    form_values = session.pop(_NOTE_FORM_VALUES_KEY, {})
    return render_template(
        "index.html",
        page_title="Dashboard",
        notes=data,
        csrf_token=_notes_csrf_token(),
        errors=errors,
        form_values=form_values,
    )

@notes_bp.route("/addNote", methods=["GET", "POST"])
@login_required
def add_note():
    if not current_user.is_authenticated:
        abort(401, description="You must be logged in to add a note.")
    if request.method == "POST":
        errors = []
        if not _has_valid_notes_csrf_token():
            errors.append("Invalid form submission.")
        if len(request.form.get("title", "")) > 50:
            errors.append("Title must be less than 50 characters.")
        if len(request.form.get("content", "")) > 1000:
            errors.append("Content must be less than 1000 characters.")
        if errors:
            return _redirect_to_index_with_errors(
                "add",
                errors,
                _submitted_note_values(),
            )

        new_note = Note(
            title=request.form.get("title"),
            content=request.form.get("content"),
            owner_id=current_user.id,
        )
        db.session.add(new_note)
        try:
            db.session.commit()
            session.pop("notes_csrf_token", None)
        except SQLAlchemyError:
            db.session.rollback()
            return _redirect_to_index_with_errors(
                "add",
                ["There was an error submitting this request. Please try again."],
                _submitted_note_values(),
            )
        return redirect(url_for("dashboards.index"))
    return redirect(url_for("dashboards.index"))


@notes_bp.route("/editNote/<int:note_id>", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = db.session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        flash("You are not authorized to edit this note.", "error")
        return redirect(url_for("dashboards.index"))
    if not note:
        flash("Note not found.", "error")
        return redirect(url_for("dashboards.index"))
    if request.method == "POST":
        errors = []
        if not _has_valid_notes_csrf_token():
            errors.append("Invalid form submission.")
        note.title = request.form.get("title", "")
        note.content = request.form.get("content", "")
        if len(note.title) > 50:
            errors.append("Title must be less than 50 characters.")
        if len(note.content) > 1000:
            errors.append("Content must be less than 1000 characters.")
        if errors:
            return _redirect_to_index_with_errors(
                note.id,
                errors,
                _submitted_note_values(),
            )
        try:
            db.session.commit()
            session.pop("notes_csrf_token", None)
            return redirect(url_for("dashboards.index"))
        except SQLAlchemyError:
            db.session.rollback()
            return _redirect_to_index_with_errors(
                note.id,
                ["There was an error submitting this request. Please try again."],
                _submitted_note_values(),
            )

@notes_bp.route("/deleteNote/<int:note_id>", methods=["GET", "POST"])
@login_required
def delete_note(note_id):
    note = db.session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        flash("You are not authorized to delete this note.", "error")
        return redirect(url_for("dashboards.index"))
    if not note:
        flash("Note not found.", "error")
        return redirect(url_for("dashboards.index"))
    if request.method == "POST":
        if not _has_valid_notes_csrf_token():
            flash("Invalid form submission.", "error")
            return redirect(url_for("dashboards.index"))

        db.session.delete(note)
        try:
            db.session.commit()
            session.pop("notes_csrf_token", None)
        except SQLAlchemyError:
            db.session.rollback()
            flash("There was an error submitting this request. Please try again.", "error")
            return redirect(url_for("dashboards.index"))
        return redirect(url_for("dashboards.index"))
    return redirect(url_for("dashboards.index"))

