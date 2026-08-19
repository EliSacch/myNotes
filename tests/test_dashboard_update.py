from app.extensions import db
from app.models import Dashboard
from tests.conftest import CSRF_TOKEN, login

JSON_HEADERS = {"X-Requested-With": "XMLHttpRequest"}


def update_path(dashboard):
    return f"/dashboards/{dashboard.id}/update"


def test_update_requires_login(client, dashboard):
    response = client.post(
        update_path(dashboard),
        data={"name": "Renamed", "csrf_token": CSRF_TOKEN},
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    assert db.session.get(Dashboard, dashboard.id).name == "Work"


def test_update_get_redirects_to_dashboard(client, user, dashboard):
    login(client, user)

    response = client.get(update_path(dashboard))

    assert response.status_code == 302
    assert response.headers["Location"].endswith(f"/dashboards/{dashboard.id}/work")


def test_update_returns_404_for_missing_dashboard(client, user):
    login(client, user)

    response = client.post(
        "/dashboards/999/update",
        data={"name": "Renamed", "csrf_token": CSRF_TOKEN},
    )

    assert response.status_code == 404


def test_update_returns_404_for_another_users_dashboard(
    client, user, other_user
):
    other_dashboard = Dashboard(
        name="Secret", owner_id=other_user.id, is_default=False
    )
    db.session.add(other_dashboard)
    db.session.commit()
    login(client, user)

    response = client.post(
        update_path(other_dashboard),
        data={"name": "Stolen", "csrf_token": CSRF_TOKEN},
    )

    assert response.status_code == 404
    assert db.session.get(Dashboard, other_dashboard.id).name == "Secret"


def test_update_rejects_renaming_default_dashboard(
    client, user, default_dashboard
):
    login(client, user)

    response = client.post(
        update_path(default_dashboard),
        data={"name": "Not Home", "csrf_token": CSRF_TOKEN},
    )

    assert response.status_code == 302
    assert db.session.get(Dashboard, default_dashboard.id).name == "Home"
    with client.session_transaction() as session:
        errors = session["dashboard_form_errors"]["update"]
        assert errors["form"] == ["You cannot rename the default dashboard."]


def test_update_rejects_renaming_default_dashboard_json(
    client, user, default_dashboard
):
    login(client, user)

    response = client.post(
        update_path(default_dashboard),
        data={"name": "Not Home", "csrf_token": CSRF_TOKEN},
        headers=JSON_HEADERS,
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["ok"] is False
    assert payload["retryable"] is False
    assert payload["errors"]["form"] == ["You cannot rename the default dashboard."]
    assert db.session.get(Dashboard, default_dashboard.id).name == "Home"


def test_update_rejects_invalid_csrf(client, user, dashboard):
    login(client, user)

    response = client.post(
        update_path(dashboard),
        data={"name": "Renamed", "csrf_token": "wrong-token"},
    )

    assert response.status_code == 302
    assert db.session.get(Dashboard, dashboard.id).name == "Work"
    with client.session_transaction() as session:
        errors = session["dashboard_form_errors"]["update"]
        assert errors["form"] == ["Invalid form submission."]


def test_update_requires_name(client, user, dashboard):
    login(client, user)

    response = client.post(
        update_path(dashboard),
        data={"name": "   ", "csrf_token": CSRF_TOKEN},
    )

    assert response.status_code == 302
    assert db.session.get(Dashboard, dashboard.id).name == "Work"
    with client.session_transaction() as session:
        errors = session["dashboard_form_errors"]["update"]
        assert errors["name"] == ["Name is required."]
        assert session["dashboard_form_values"]["update"]["name"] == "   "


def test_update_rejects_name_longer_than_50_characters(client, user, dashboard):
    login(client, user)
    too_long = "a" * 51

    response = client.post(
        update_path(dashboard),
        data={"name": too_long, "csrf_token": CSRF_TOKEN},
        headers=JSON_HEADERS,
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["errors"]["name"] == ["Name must be less than 50 characters."]
    assert db.session.get(Dashboard, dashboard.id).name == "Work"


def test_update_rejects_duplicate_name_for_same_owner(client, user, dashboard):
    other = Dashboard(name="Personal", owner_id=user.id, is_default=False)
    db.session.add(other)
    db.session.commit()
    login(client, user)

    response = client.post(
        update_path(dashboard),
        data={"name": "Personal", "csrf_token": CSRF_TOKEN},
        headers=JSON_HEADERS,
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["errors"]["name"] == ["You already have a dashboard with this name."]
    assert db.session.get(Dashboard, dashboard.id).name == "Work"


def test_update_renames_dashboard_and_redirects(client, user, dashboard):
    login(client, user)

    response = client.post(
        update_path(dashboard),
        data={"name": "My Board", "csrf_token": CSRF_TOKEN},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        f"/dashboards/{dashboard.id}/my-board"
    )
    updated = db.session.get(Dashboard, dashboard.id)
    assert updated.name == "My Board"
    with client.session_transaction() as session:
        assert "dashboards_csrf_token" not in session
        flashes = session.get("_flashes", [])
        assert ("success", "Dashboard updated successfully.") in flashes


def test_update_renames_dashboard_json(client, user, dashboard):
    login(client, user)

    response = client.post(
        update_path(dashboard),
        data={"name": "Ideas", "csrf_token": CSRF_TOKEN},
        headers=JSON_HEADERS,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["redirect_url"].endswith(f"/dashboards/{dashboard.id}/ideas")
    assert db.session.get(Dashboard, dashboard.id).name == "Ideas"
