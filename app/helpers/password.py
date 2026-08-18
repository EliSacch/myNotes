COMMON_PASSWORDS = {"password", "password123", "qwerty", "letmein", "12345678"}


def collect_password_errors(password, confirm_password="", username="", email=""):
    password_errors = []
    confirm_password_errors = []

    if not 12 <= len(password) <= 128:
        password_errors.append("Password must be between 12 and 128 characters.")
    if password != confirm_password:
        confirm_password_errors.append("Passwords do not match.")
    if password.casefold() in COMMON_PASSWORDS:
        password_errors.append("Choose a less common password.")
    if password and not any(character.islower() for character in password):
        password_errors.append("Password must include a lowercase letter.")
    if password and not any(character.isupper() for character in password):
        password_errors.append("Password must include an uppercase letter.")
    if password and not any(character.isdigit() for character in password):
        password_errors.append("Password must include a number.")
    if password and not any(not character.isalnum() for character in password):
        password_errors.append("Password must include a symbol.")
    if username and username.casefold() in password.casefold():
        password_errors.append("Password must not contain your username.")
    email_local_part = email.partition("@")[0]
    if email_local_part and email_local_part.casefold() in password.casefold():
        password_errors.append("Password must not contain your email address.")

    return password_errors, confirm_password_errors
