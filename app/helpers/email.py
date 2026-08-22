import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def collect_email_errors(email):
    errors = []
    if len(email) > 100 or not EMAIL_PATTERN.fullmatch(email):
        errors.append("Enter a valid email address.")
    return errors
