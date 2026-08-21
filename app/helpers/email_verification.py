from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from flask import current_app

SALT = "email-verify"
MAX_AGE_SECONDS = 60 * 60 * 24  # 24 hours

def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=SALT)

def generate_email_token(user):
    return _serializer().dumps({"user_id": user.id, "email": user.email})

def load_email_token(token):
    try:
        return _serializer().loads(token, max_age=MAX_AGE_SECONDS)
    except SignatureExpired:
        return "expired"
    except BadSignature:
        return None