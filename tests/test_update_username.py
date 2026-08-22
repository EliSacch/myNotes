from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import User
from tests.conftest import login

PROFILE_CSRF = "test-profile-csrf-token"


def login_profile(client, user):
    login(client, user)
    with client.session_transaction() as session:
        session["profile_csrf_token"] = PROFILE_CSRF


def update_path(user):
    return f"/profile/{user.id}/update-username"


def flashes(client):
    with client.session_transaction() as session:
        return session.get("_flashes", [])


def test_update_username_requires_login(client, user):
    response = client.post(
        update_path(user),
        data={"username": "newname", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    assert db.session.get(User, user.id).username == "elisa"


def test_update_username_returns_404_for_missing_user(client, user):
    login_profile(client, user)

    response = client.post(
        "/profile/999/update-username",
        data={"username": "newname", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 404


def test_update_username_returns_403_for_another_user(client, user, other_user):
    login_profile(client, user)

    response = client.post(
        update_path(other_user),
        data={"username": "stolen", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 403
    assert db.session.get(User, other_user.id).username == "other"


def test_update_username_flashes_invalid_csrf(client, user):
    login_profile(client, user)

    response = client.post(
        update_path(user),
        data={"username": "newname", "csrf_token": "wrong-token"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile/")
    assert db.session.get(User, user.id).username == "elisa"
    assert ("warning", "Your form has expired. Please try again.") in flashes(client)
    with client.session_transaction() as session:
        assert "username_form_errors" not in session


def test_update_username_shows_validation_errors_under_field(client, user):
    login_profile(client, user)

    response = client.post(
        update_path(user),
        data={"username": "ab", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 302
    assert db.session.get(User, user.id).username == "elisa"
    assert flashes(client) == []
    with client.session_transaction() as session:
        assert session["username_form_errors"]["username"] == [
            "Username must be between 3 and 50 characters."
        ]
        assert session["username_form_values"]["username"] == "ab"


def test_update_username_shows_duplicate_under_field(client, user, other_user):
    login_profile(client, user)

    response = client.post(
        update_path(user),
        data={"username": "other", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 302
    assert db.session.get(User, user.id).username == "elisa"
    assert flashes(client) == []
    with client.session_transaction() as session:
        assert session["username_form_errors"]["username"] == [
            "Username already exists."
        ]


def test_update_username_flashes_database_error(client, user):
    login_profile(client, user)

    with patch(
        "app.routes.profile.db.session.commit",
        side_effect=SQLAlchemyError(),
    ):
        response = client.post(
            update_path(user),
            data={"username": "newname", "csrf_token": PROFILE_CSRF},
        )

    assert response.status_code == 302
    assert db.session.get(User, user.id).username == "elisa"
    assert (
        "error",
        "There was an error submitting this request. Please try again.",
    ) in flashes(client)
    with client.session_transaction() as session:
        assert "username_form_errors" not in session


def test_update_username_saves_and_flashes_success(client, user):
    login_profile(client, user)

    response = client.post(
        update_path(user),
        data={"username": "newname", "csrf_token": PROFILE_CSRF},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile/")
    assert db.session.get(User, user.id).username == "newname"
    assert ("success", "Username updated successfully.") in flashes(client)
    with client.session_transaction() as session:
        assert "profile_csrf_token" not in session


def test_profile_renders_username_field_errors(client, user):
    login_profile(client, user)
    with client.session_transaction() as session:
        session["username_form_errors"] = {
            "username": ["Username must be between 3 and 50 characters."]
        }
        session["username_form_values"] = {"username": "ab"}

    response = client.get("/profile/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Username must be between 3 and 50 characters." in html
    assert 'value="ab"' in html
    assert 'profile-inline-view hidden-form' in html
    assert 'profile-inline-edit hidden-form' not in html
