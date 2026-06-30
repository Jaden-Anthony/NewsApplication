# NewsApp — Django Capstone Project

A role-based news publishing platform built with Django. Supports three user
roles — **Journalist**, **Editor**, and **Reader** — each with dedicated
dashboards, CRUD operations, subscription management, and a REST API feed.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.8 or newer |
| pip | latest |
| Git | any recent version |
| MariaDB / MySQL | 10.x or newer (for production database) |
| Docker *(optional)* | 20.x or newer |

---

## Option 1 — Run with a Virtual Environment (venv)

### 1. Clone the repository

```bash
git clone https://github.com/Jaden-Anthony/NewsApplication.git
cd NewsApplication
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the database

The project is configured to use **MariaDB / MySQL**. Open
`config/settings.py` and update the `DATABASES` section with your local
credentials:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "news_application_db",   # Create this database first
        "USER": "root",                  # Your MariaDB username
        "PASSWORD": "your_password",     # Your MariaDB password
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}
```

> **Important:** Create the database before running migrations:
> ```sql
> CREATE DATABASE news_application_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
> ```

If you prefer SQLite for quick local testing, replace the `DATABASES` block
with:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

### 7. Start the development server

```bash
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000/**.

---

## Option 2 — Run with Docker

The image is publicly available on Docker Hub — no build step required.

### 2a. Pull and run from Docker Hub *(fastest — no source code needed)*

```bash
docker pull jade46/newsapp:latest
docker run -p 8000:8000 -e DB_ENGINE=sqlite3 jade46/newsapp:latest
```

Open your browser at **http://127.0.0.1:8000/**.

> Docker Hub: https://hub.docker.com/r/jade46/newsapp

### 2b. Build locally from source

```bash
docker build -t jade46/newsapp .
docker run -p 8000:8000 -e DB_ENGINE=sqlite3 jade46/newsapp
```

### Notes

- `DB_ENGINE=sqlite3` runs the app with SQLite — no MySQL server needed.
  Migrations are applied automatically when the container starts.
- To use MySQL instead, omit `DB_ENGINE` and pass the DB env vars listed
  in the Security Notice section below.
- To create an admin account inside the running container:
  ```bash
  docker exec -it <container_id> python manage.py createsuperuser
  ```
- To run the test suite inside Docker:
  ```bash
  docker run --rm -e DB_ENGINE=sqlite3 jade46/newsapp:latest python manage.py test NewsApplication --verbosity=2
  ```

---

## API Endpoint

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/feed/` | Returns a JSON list of approved articles from journalists the authenticated reader subscribes to. |

**Authentication:** The API uses session or basic authentication. Log in via
the web interface first, or include credentials in your request:

```bash
curl -u username:password http://127.0.0.1:8000/api/feed/
```

---

## Project Structure

```
NewsApp/
├── config/             # Django project settings, URLs, WSGI
├── NewsApplication/    # Main app (models, views, templates, forms)
│   ├── templates/      # HTML templates
│   ├── models.py       # Article, Newsletter, Publisher, CustomUser
│   ├── views.py        # Class-based views and API views
│   ├── forms.py        # Registration, article, newsletter forms
│   ├── serializers.py  # DRF serializers for the API
│   └── urls.py         # URL routing
├── docs/               # Sphinx documentation (auto-generated)
├── Dockerfile          # Container configuration
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Security Notice

> **Do not** commit database passwords, secret keys, or API tokens to a
> public repository. Update `SECRET_KEY` and database credentials in
> `config/settings.py` with your own values before deploying.

---

## License & Credits

This project was created as part of the HyperionDev Software Engineering
Bootcamp capstone. Adjust or add a license file if you intend to publish it.
