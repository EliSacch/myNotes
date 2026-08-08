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
  - For a local deployment follow these steps:
    - Clone the repository
    - Create a new vistual environment `python3 -m venv .`
    - Activate virtual environment `source ./bin/activate`
    - Install packages from requirements.txt `pip install -r requirements.txt`
    - Create a PostgreSQL database and configure its URL. Copy `.env.example` to a local `.env` file, replace the placeholder values, then load it with `export DATABASE_URL="$(grep '^DATABASE_URL=' .env | cut -d= -f2-)"`.
    - Alternatively, set `DATABASE_URL` directly in your terminal. Its expected format is `postgresql+psycopg2://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME`.

    - 
    - Run locally using `python run.py`.


  - To stop running locally
    - brew services stop postgresql@14
    - Deactivate virtual environment `deactivate`

  
  #### Create a Postgres Local db for the first time
  - Install postgresql `brew install postgresql@18`
  - Start `brew services start postgresql@18`
  - Login with admin role
  - Create new user `CREATE ROLE mynotes_user LOGIN;`
  - Set password `\password mynotes_user`
  - Create a db `CREATE DATABASE mynotes OWNER mynotes_user;`
  - Choose a new password when prompted then exit `\q`
  - Login with new user `/opt/homebrew/opt/postgresql@18/bin/psql -U mynotes_user -d mynotes -W`



### Environment variables

The app requires `DATABASE_URL` to connect to PostgreSQL. Store it in the hosting provider's secret/configuration settings when deploying; never commit an actual connection URL or password. The committed `.env.example` only documents the required format.

[Back to the top](#myNotes)

## Credits 

### Design

- The color palette was generated using [My color Space](https://mycolor.space/)

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
