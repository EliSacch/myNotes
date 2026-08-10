# myNotes
A web app for your notes and lists

[Link to live site]()

![Hero image]()


## Table of content

- [Design and User Experience](#design-and-user-experience)
  - [User Stories](#user-stories)
  - [Flow Chart](#flow-chart)
  - [Wireframes](#wireframes)
  - [Design](#design)

- [Architecture](#architecture)

- [Features](#features)

- [Testing](#testing)
  - [Tests](#tests)
  - [Validator Testing](#validator-testing)
  - [Fixed bugs](#fixed-bugs)
  - [Unfixed bugs](#unfixed-bugs)

- [Deployment](#deployment)
  - [Live Website](#live-website)
  - [Local Deployment](#local-deployment)

- [Credits](#credits)
  - [Code](#code)

- [Technologies used](#technologies-used)

- [Acknowledgements](#acknowledgements)

## Design and User Experience


### User Stories
- As a first time use I want:
    - To understand the purpose of the website.
    - To easily understand how to use it.
    - To have a clear a compact design to quickly take notes without eccessive navigation.
- As a frequent user I want:
    - To have a personal profile where I can save my notes.
    - To be able to access my notes from all my devices.


### Flow Chart

To develop a program that answers all the needs identified above, I have created the following flow chart:

![Flow_Chart]()

[Back to the top](#myNotes)

### Wireframes

<details>
  <summary>Mobile</summary>

![Home](media/wireframes/mobile-home.png)
![Add note](media/wireframes/mobile-note.png)
![Add list](media/wireframes/mobile-list.png)

</details>


<details>
  <summary>Desktop</summary>

![Home](media/wireframes/desktop-home.png)
![Add note](media/wireframes/desktop-note.png)
![Add list](media/wireframes/desktop-list.png)

</details>

### Design

For the color I opted for a neutral palette

![Color Palette](media/palette.png)

## Architecture

App built following the Application Factory Pattern

## Features 

## Testing 

### Tests

  <details>
  <summary>Manual testing</summary>

  |Action | Expected behavious | Pass / Fail|
  |-------|--------------------|-------|
  | |  | Pass |
  | |  | Pass |

  </details>

- JS testing


[Back to the top](#myNotes)

### Validator Testing

html
css
The PEP8 

### Fixed Bugs


[Back to the top](#myNotes)

### Unfixed Bugs

- There are no known unfixed bugs.


## Deployment

### Live Website

The live version of this program is available on Heroku.

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
    - `brew services stop postgresql@18`
    - Deactivate virtual environment `deactivate`

  
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

[Back to the top](#myNotes)

## Credits 

### Design

### Code


## Technologies used

### Main languages

    - Flask
    - Python
    - Postgres
    - OAuth

### Python Libraries

  - sys - needed in 

## Acknowledgements
