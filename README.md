# myNotes
A web app for your notes

[Link to live site]()

![Hero image]()


## Table of content

- [Architecture](#architecture)

- [Features](#features)

- [Accessibility](#accessibility)

- [Testing](#testing)
  - [Tests](#tests)
  - [Validator Testing](#validator-testing)
  - [Fixed bugs](#fixed-bugs)
  - [Unfixed bugs](#unfixed-bugs)

- [Deployment](#deployment)
  - [Live Website](#live-website)
  - [Local Deployment](#local-deployment)
  - [Database migrations](#database-migrations)
  - [Environment variables](#environment-variables)
  - [Formatting templates](#formatting-templates)

- [Technologies used](#technologies-used)
  - [Languages](#languages)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Tooling](#tooling)
  - [Hosting](#hosting)

- [Acknowledgements](#acknowledgements)


## Architecture

App built following the Application Factory Pattern

[Back to the top](#myNotes)

## Features 

[Back to the top](#myNotes)

## Accessibility

The UI is built with keyboard and screen-reader use in mind. Highlights:

- **Landmarks** — `lang` on `<html>`, a skip link to `#main-content`, labelled `<nav>` regions, and a single primary page `<h1>`.
- **Names** — Icon-only controls use `aria-label`; decorative Font Awesome icons use `aria-hidden="true"`. Tooltips are visual aids only and also show on `:focus-within`.
- **Forms** — Inputs have real labels; validation uses `aria-invalid`, `aria-describedby`, and `role="alert"`, with focus moved to the error or invalid field.
- **Dialogs** — Modals use `role="dialog"`, `aria-modal`, `aria-labelledby`, background `inert` while open, Escape to close, and focus return to the trigger. Dialog titles are `<h2>`.
- **Menus** — Options and dashboards toggles expose `aria-expanded` / `aria-controls`, close on Escape (and outside click), and manage focus on open/close.
- **Focus** — Global `:focus-visible` outlines. Opening add/edit note focuses the title after Editor.js is ready (`autofocus: false`) so the field is actually editable.
- **Live updates** — Flash messages use `role="status"` / `aria-live`. Async checklist toggle failures announce via `#a11y-status`.
- **Motion** — Page transitions, menus, and tooltips respect `prefers-reduced-motion`.

Editor.js checklists are enhanced for keyboard use (Tab between items; Space/Enter on checkboxes).

During development, Cursor loads project accessibility guidance from `.cursor/rules/accessibility.mdc`. For a full review, use the project skill in `.cursor/skills/accessibility-audit/` (e.g. ask the agent to run an accessibility audit).

[Back to the top](#myNotes)

## Testing 

### Validator Testing

### Fixed Bugs


### Unfixed Bugs

- There are no known unfixed bugs.

[Back to the top](#myNotes)

## Deployment

### Live Website

The live version of this program is available here.

[Click here to open]()


### Local Deployment
  - For first time local deployment follow these steps:
    - Clone the repository
    - Create a new vistual environment `python3 -m venv .`
    - Activate virtual environment `source ./bin/activate`
    - Install packages from requirements.txt `pip install -r requirements.txt`
    - Create a PostgreSQL database and configure its URL. Copy `.env.example` to a local `.env` file, then replace the `DATABASE_URL` and `SECRET_KEY` placeholder values.
    - Load both values into your terminal:
      ```bash
      export DATABASE_URL="$(grep '^DATABASE_URL=' .env | cut -d= -f2-)"
      export SECRET_KEY="$(grep '^SECRET_KEY=' .env | cut -d= -f2-)"
      ```
    - Alternatively, set `DATABASE_URL` and `SECRET_KEY` directly in your terminal. The database URL format is `postgresql+psycopg2://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME`.
    - Create or update the database schema with `flask --app run db upgrade`.
    - Run locally using `python run.py`

  - For susequent runs simply:
    - Start postgres `brew services stop postgresql@18`
    - Activate virtual environment `source ./bin/activate`
    - Load env vars into your terminal:
      ```bash
      export DATABASE_URL="$(grep '^DATABASE_URL=' .env | cut -d= -f2-)"
      export SECRET_KEY="$(grep '^SECRET_KEY=' .env | cut -d= -f2-)"
      ```
    - Run locally using `python run.py`


  - To stop running locally
    - Ctrl + C
    - Deactivate virtual environment `deactivate`
    - Quit postgres `\q`
    - Stop postgres `brew services stop postgresql@18`

  
  #### Create a Postgres Local db for the first time
  - Install postgresql `brew install postgresql@18`
  - Start `brew services start postgresql@18`
  - List users `\du+`
  - Login with admin role `/opt/homebrew/opt/postgresql@18/bin/psql -d postgres`
  - Check current user `SELECT current_user;`
  - Create new user `CREATE ROLE mynotes_user LOGIN PASSWORD 'choose-a-new-password';`
  - Create a db `CREATE DATABASE mynotes OWNER mynotes_user;`
  - Exit `\q`
  - Restore secure local authentication in `/opt/homebrew/var/postgresql@18/pg_hba.conf` by changing both trust values back to `scram-sha-256`
  - then restart `brew services restart postgresql@18`
  - Login with new user `/opt/homebrew/opt/postgresql@18/bin/psql -U mynotes_user -d mynotes -W`


### Database migrations

Database schema changes are tracked with Flask-Migrate and Alembic. Run all migration commands after loading `DATABASE_URL` and `SECRET_KEY`.

1. Update the SQLAlchemy model(s).
2. Generate a migration:
   ```bash
   flask --app run db migrate -m "describe the schema change"
   ```
3. Review the new file in `migrations/versions/` before applying it.
4. Apply the migration:
   ```bash
   flask --app run db upgrade
   ```

Never edit an already-applied migration. Create a new migration for every later schema change, and back up production data before running `db upgrade`.


### Environment variables

The app requires `DATABASE_URL` to connect to PostgreSQL and `SECRET_KEY` to securely sign sessions and CSRF tokens. Store both in the hosting provider's secret/configuration settings when deploying; never commit an actual connection URL, password, or secret key. The committed `.env.example` only documents the required format.

### Formatting templates

Jinja templates are linted and formatted with [djLint](https://djlint.com/). Defaults live in `pyproject.toml` (`profile = "jinja"`, `files = ["app/templates"]`).

With the virtual environment activated:

```bash
# Check formatting without changing files
djlint - --check

# Reformat templates
djlint - --reformat

# Lint templates
djlint - --lint
```

The `-` source is required when `files` is set in the config; djLint then uses `app/templates` automatically.

In Cursor/VS Code, install the djLint extension and set it as the default formatter for Jinja/HTML files if you want format-on-save.

[Back to the top](#myNotes)

## Technologies used

### Languages

- Python
- HTML / Jinja2 templates
- CSS
- JavaScript

### Backend

- [Flask](https://flask.palletsprojects.com/) — web framework (application factory pattern)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) — ORM integration
- [SQLAlchemy](https://www.sqlalchemy.org/) — database models and queries
- [Flask-Migrate](https://flask-migrate.readthedocs.io/) / [Alembic](https://alembic.sqlalchemy.org/) — database migrations
- [Flask-Login](https://flask-login.readthedocs.io/) — session-based authentication
- [Flask-Limiter](https://flask-limiter.readthedocs.io/) — rate limiting on auth routes
- [Werkzeug](https://werkzeug.palletsprojects.com/) — password hashing
- [psycopg2](https://www.psycopg.org/) — PostgreSQL driver
- [PostgreSQL](https://www.postgresql.org/) — primary database

### Frontend

- [Jinja2](https://jinja.palletsprojects.com/) — server-rendered templates
- [Editor.js](https://editorjs.io/) — block-style note content editing (paragraphs and checklists)
- [jQuery](https://jquery.com/) — client-side interactions (modals, forms, options menu)
- [Font Awesome](https://fontawesome.com/) — icons
- [Google Fonts](https://fonts.google.com/) — Mulish and Shadows Into Light

### Tooling

- [Cursor](https://cursor.com/) — AI-assisted development (rules and skills for accessibility and workflows)
- [djLint](https://djlint.com/) — Jinja/HTML template linting and formatting
- Virtualenv — local Python environment

### Hosting

- [TBD]() — planned/live deployment target

## Acknowledgements
