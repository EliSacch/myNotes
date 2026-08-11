import hmac
import secrets

from flask import Blueprint, abort, flash, jsonify, redirect, request, session, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Dashboard, Note

notes_bp = Blueprint("notes", __name__, url_prefix="/dashboards/<int:dashboard_id>/<slug>/notes")
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
    return redirect(url_for("index.index"))


def _submitted_note_values():
    return {
        "title": request.form.get("title", ""),
        "content": request.form.get("content", ""),
    }


def _get_owned_dashboard(dashboard_id, slug):
    dashboard = db.session.get(Dashboard, dashboard_id)
    if not dashboard or dashboard.owner_id != current_user.id:
        abort(404)
    if dashboard.slug != slug:
        abort(404)
    return dashboard


@notes_bp.route("/list")
@login_required
def list_notes(dashboard_id, slug):
    _get_owned_dashboard(dashboard_id, slug)
    notes = db.session.scalars(
        db.select(Note)
        .where(Note.dashboard_id == dashboard_id)
        .order_by(Note.created_at.asc())
    )
    return jsonify([note.to_dict() for note in notes])

@notes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_note(dashboard_id, slug):
    dashboard = _get_owned_dashboard(dashboard_id, slug)
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
            dashboard_id=dashboard.id,
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
        return redirect(url_for("index.index"))
    return redirect(url_for("index.index"))


@notes_bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(dashboard_id, slug, note_id):
    dashboard = _get_owned_dashboard(dashboard_id, slug)
    note = db.session.get(Note, note_id)
    if not note or note.owner_id != current_user.id or note.dashboard_id != dashboard.id:
        flash("You are not authorized to edit this note.", "error")
        return redirect(url_for("index.index"))
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
            return redirect(url_for("index.index"))
        except SQLAlchemyError:
            db.session.rollback()
            return _redirect_to_index_with_errors(
                note.id,
                ["There was an error submitting this request. Please try again."],
                _submitted_note_values(),
            )
    return redirect(url_for("index.index"))

@notes_bp.route("/<int:note_id>/delete", methods=["GET", "POST"])
@login_required
def delete_note(dashboard_id, slug, note_id):
    dashboard = _get_owned_dashboard(dashboard_id, slug)
    note = db.session.get(Note, note_id)
    if not note or note.owner_id != current_user.id or note.dashboard_id != dashboard.id:
        flash("You are not authorized to delete this note.", "error")
        return redirect(url_for("index.index"))
    if request.method == "POST":
        if not _has_valid_notes_csrf_token():
            flash("Invalid form submission.", "error")
            return redirect(url_for("index.index"))

        db.session.delete(note)
        try:
            db.session.commit()
            session.pop("notes_csrf_token", None)
        except SQLAlchemyError:
            db.session.rollback()
            flash("There was an error submitting this request. Please try again.", "error")
            return redirect(url_for("index.index"))
        return redirect(url_for("index.index"))
    return redirect(url_for("index.index"))
