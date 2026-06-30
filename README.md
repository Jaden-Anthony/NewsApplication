# NewsApp — Capstone Project (Final)

This repository contains the finalised NewsApp Django project for the Level 2 Capstone.

## Overview

- **Project:** NewsApp
- **Framework:** Django
- **Purpose:** A simple news publishing platform with roles (journalist, editor, reader), article CRUD, publisher management, subscriptions and a small API feed endpoint.

## Prerequisites

- Python 3.8 or newer
- pip
- git

Optional but recommended:
- Create and use a virtual environment (`venv` or `virtualenv`).

## Quick setup

Open a terminal and run the commands below from the project root (the folder that contains `manage.py`). Example path in this workspace:

[NewsApp/manage.py](Level 2 - Introduction to Software Engineering/M06T08 – Capstone Project – News Application/Capstone Project/NewsApp/manage.py#L1)

Commands (Windows PowerShell / bash):

```bash
cd "c:\Users\Jaden\OneDrive\Desktop\JA25030017630\Level 2 - Introduction to Software Engineering\M06T08 – Capstone Project – News Application\Capstone Project\NewsApp"
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# or on bash: source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Apply migrations and create a superuser (follow prompts)
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

The app will be available at http://127.0.0.1:8000/ by default.

## Running tests (if any)

If this project contains Django tests, run:

```bash
python manage.py test
```

## API endpoint(s)

This project exposes one primary API endpoint for subscribed article feeds:

- GET `/api/feed/` — subscribed article feed (class: `SubscribedArticleFeedAPI`)

Example curl request:

```bash
curl -i http://127.0.0.1:8000/api/feed/
```

Notes:
- If the API requires authentication (session or token), authenticate first (login via the site or obtain a token), then include cookies or Authorization headers in your request.
- You can also test the endpoint in the browser at http://127.0.0.1:8000/api/feed/ while logged in.

## Populate sample data

- Use the Django admin (http://127.0.0.1:8000/admin/) to create articles, publishers and users.
- Ensure at least one published article exists so the feed returns results.

## Common troubleshooting

- If migrations fail, ensure the virtual environment is active and dependencies are installed.
- If port `8000` is already in use, run `python manage.py runserver 0.0.0.0:8001` (or another port).

## License & Credits

This project was created as part of the Level 2 Capstone. Adjust or add a license file if you intend to publish it.

---

If you want, I can also:

- run the server and verify the feed endpoint locally
- add example Postman requests or a small test script to query the API

# NewsApp Capstone Project

This is the Django News Application capstone project. It includes custom user registration and login, article and newsletter management, publisher staff functionality, and reader subscriptions.

## What is included

- Django 6.0.6 project setup
- `NewsApplication` app with:
  - custom `CustomUser` model
  - article creation, update, delete, and detail views
  - publisher management and staff pages
  - newsletter creation and management
  - login, logout, and registration templates
- SQLite database configuration for local development
- simple templates under `NewsApplication/templates/NewsApplication`

## Requirements

The project uses the following packages:

- Django==6.0.6
- asgiref==3.11.1
- sqlparse==0.5.5
- tzdata==2026.2

Install them from the project `requirements.txt`.

## Setup

1. Open a terminal in the project root:
   ```powershell
   cd "C:\Users\Jaden\OneDrive\Desktop\JA25030017630\Level 2 - Introduction to Software Engineering\M06T08 – Capstone Project - News Application\Capstone Project\NewsApp"
   ```

2. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```powershell
   python manage.py migrate
   ```

5. Create a superuser (optional, for admin access):
   ```powershell
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```powershell
   python manage.py runserver
   ```

7. Open the app in your browser:
   ```text
   http://127.0.0.1:8000/
   ```

## Notes

- Do not commit secret keys or database files.
- The project is configured for local development with SQLite.
- If you want to reset the database, delete `db.sqlite3` and rerun `python manage.py migrate`.
