import smtplib
from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.helpers.email_verification import load_email_token
from app.models import User
from tests.conftest import login
from tests.test_email_verification import confirm_url_token, mail_outbox

PROFILE_CSRF = "test-profile-csrf-token"


def login_profile(client, user):
    login(client, user)
    with client.session_transaction() as session:
        session["profile_csrf_token"] = PROFILE_CSRF


def update_path(user):
    return f"/profile/{user.id}/update-email"


def flashes(client):
    with client.session_transaction() as session:
        return session.get("_flashes", [])


def test_update_email_requires_login(client, user):
    response = client.post(
        update_path(user),
        data={"email": "new@example.com", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    assert db.session.get(User, user.id).email == "elisa@example.com"


def test_update_email_returns_404_for_missing_user(client, user):
    login_profile(client, user)

    response = client.post(
        "/profile/999/update-email",
        data={"email": "new@example.com", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 404


def test_update_email_returns_403_for_another_user(client, user, other_user):
    login_profile(client, user)

    response = client.post(
        update_path(other_user),
        data={"email": "stolen@example.com", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 403
    assert db.session.get(User, other_user.id).email == "other@example.com"


def test_update_email_flashes_invalid_csrf(client, user):
    login_profile(client, user)

    response = client.post(
        update_path(user),
        data={"email": "new@example.com", "csrf_token": "wrong-token"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile/")
    assert db.session.get(User, user.id).email == "elisa@example.com"
    assert ("warning", "Your form has expired. Please try again.") in flashes(client)
    with client.session_transaction() as session:
        assert "email_form_errors" not in session


def test_update_email_shows_validation_errors_under_field(client, user):
    login_profile(client, user)

    response = client.post(
        update_path(user),
        data={"email": "not-an-email", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 302
    assert db.session.get(User, user.id).email == "elisa@example.com"
    assert flashes(client) == []
    with client.session_transaction() as session:
        assert session["email_form_errors"]["email"] == [
            "Enter a valid email address."
        ]
        assert session["email_form_values"]["email"] == "not-an-email"


def test_update_email_shows_duplicate_under_field(client, user, other_user):
    login_profile(client, user)

    response = client.post(
        update_path(user),
        data={"email": "other@example.com", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 302
    assert db.session.get(User, user.id).email == "elisa@example.com"
    assert flashes(client) == []
    with client.session_transaction() as session:
        assert session["email_form_errors"]["email"] == [
            "Email already exists."
        ]


def test_update_email_flashes_database_error(client, user):
    login_profile(client, user)

    with patch(
        "app.routes.profile.db.session.commit",
        side_effect=SQLAlchemyError(),
    ):
        response = client.post(
            update_path(user),
            data={"email": "new@example.com", "csrf_token": PROFILE_CSRF},
        )

    assert response.status_code == 302
    assert db.session.get(User, user.id).email == "elisa@example.com"
    assert (
        "error",
        "There was an error submitting this request. Please try again.",
    ) in flashes(client)
    with client.session_transaction() as session:
        assert "email_form_errors" not in session


def test_update_email_saves_and_sends_verification(client, app, user):
    login_profile(client, user)
    user.email_verified = True
    db.session.commit()

    response = client.post(
        update_path(user),
        data={"email": "New@example.com", "csrf_token": PROFILE_CSRF},
    )
    outbox = mail_outbox(app)
    updated = db.session.get(User, user.id)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile/")
    assert updated.email == "new@example.com"
    assert updated.email_verified is False
    assert ("success", "Email updated successfully.") in flashes(client)
    assert (
        "info",
        "Please check your email for a verification link.",
    ) in flashes(client)
    assert len(outbox) == 1
    assert outbox[0].to == ["new@example.com"]
    assert "Verify your PinIt email" in outbox[0].subject
    token = confirm_url_token(outbox[0])
    assert load_email_token(token) == {
        "user_id": user.id,
        "email": "new@example.com",
    }
    with client.session_transaction() as session:
        assert "profile_csrf_token" not in session


def test_update_email_skips_verification_when_unchanged(client, app, user):
    login_profile(client, user)
    user.email_verified = True
    db.session.commit()

    response = client.post(
        update_path(user),
        data={"email": "ELISA@example.com", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 302
    updated = db.session.get(User, user.id)
    assert updated.email == "elisa@example.com"
    assert updated.email_verified is True
    assert mail_outbox(app) == []
    assert ("success", "Email updated successfully.") in flashes(client)
    assert (
        "info",
        "Please check your email for a verification link.",
    ) not in flashes(client)


def test_update_email_keeps_change_if_send_fails(client, app, user):
    login_profile(client, user)
    user.email_verified = True
    db.session.commit()

    with patch(
        "app.routes.profile.send_verification_email",
        side_effect=smtplib.SMTPException("smtp down"),
    ):
        response = client.post(
            update_path(user),
            data={"email": "new@example.com", "csrf_token": PROFILE_CSRF},
        )

    updated = db.session.get(User, user.id)
    assert response.status_code == 302
    assert updated.email == "new@example.com"
    assert updated.email_verified is False
    assert mail_outbox(app) == []
    assert ("success", "Email updated successfully.") in flashes(client)
    assert (
        "warning",
        "We could not send the verification email. Please try again later.",
    ) in flashes(client)


def test_profile_renders_email_field_errors(client, user):
    login_profile(client, user)
    with client.session_transaction() as session:
        session["email_form_errors"] = {
            "email": ["Enter a valid email address."]
        }
        session["email_form_values"] = {"email": "not-an-email"}

    response = client.get("/profile/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Enter a valid email address." in html
    assert 'value="not-an-email"' in html
    assert 'aria-controls="update-email-form"' in html
    assert 'id="update-email-form"' in html
    assert 'profile-inline-edit-btn' in html
