from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.routes.auth import resend_verification_csrf_token

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/")
@login_required
def index():
    return render_template(
        "profile/index.html",
        user=current_user,
        csrf_token=resend_verification_csrf_token(),
    )