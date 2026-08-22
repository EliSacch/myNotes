import re

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")


def collect_username_errors(username):
    errors = []
    if not 3 <= len(username) <= 50:
        errors.append("Username must be between 3 and 50 characters.")
    elif not USERNAME_PATTERN.fullmatch(username):
        errors.append("Username may contain only letters, numbers, and underscores.")
    return errors
