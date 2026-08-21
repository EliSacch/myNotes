import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()


def _env_flag(name, default="false"):
    return os.environ.get(name, default).lower() in ("1", "true", "yes")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5001")),
        debug=_env_flag("FLASK_DEBUG"),
    )
