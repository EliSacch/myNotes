import os

from sqlalchemy import create_engine


def database_credentials():
    """Create the database engine from the host-provided connection URL."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. Set it to your PostgreSQL connection URL."
        )

    return create_engine(database_url)
