# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run dev server
FLASK_APP=run.py flask run --debug

# Database migrations
FLASK_APP=run.py flask db migrate -m "description"
FLASK_APP=run.py flask db upgrade

# Install dependencies
pip install -r requirements.txt
```

## Architecture

Flask MVC app (Spanish UI) connecting professionals with clients. SQLite database via SQLAlchemy.

**App factory** in `app/__init__.py` — `create_app()` initializes extensions and registers blueprints. Extensions (db, migrate, login_manager, csrf) are instantiated in `app/extensions.py` to avoid circular imports.

**Layers:**
- `app/controllers/` — Flask Blueprints. Each file defines a Blueprint registered in `create_app()`. Routes live here, not in models or services.
- `app/models/` — SQLAlchemy models. All models must be imported in `app/models/__init__.py` so Alembic detects them for migrations.
- `app/forms/` — Flask-WTF form classes with validation logic.
- `app/services/` — Business logic (currently empty, use when controllers get complex).
- `app/templates/` — Jinja2 templates. `layouts/base.html` is the shared layout. Subdirectories match blueprint names (`public/`, `auth/`).

**Landing page generator:** `app/controllers/landing.py` lets authenticated users request AI-generated landing pages. Prompt templates live in `app/sectors/{sector}/prompt.txt` and are filled with user input via `str.format()`. Current sectors: `abogatap`, `segurotap`, `inmotap`, `saludtap`. The `LandingRequest` model stores the request data and generated output.

**Blueprints:** `public` (home, about, contact, professional listings), `auth` (login/register), `dashboard` (profile + services CRUD), `landing` (landing page generator).

**Key relationships:** User ↔ Professional (one-to-one via `user_id` FK), Professional → Service (one-to-many via `professional_id` FK), User → LandingRequest (one-to-many via `user_id` FK).

**Auth:** Flask-Login handles sessions. Passwords hashed with `werkzeug.security`. Login-required redirects go to `auth.login`. The `current_user` proxy is available in all templates. CSRF protection is enabled globally via Flask-WTF's `CSRFProtect`.

**Config:** `config.py` reads `SECRET_KEY` and `DATABASE_URL` from env vars with dev defaults. DB file is `app.db` at project root.

## Conventions

- All user-facing text is in **Spanish**.
- Templates extend `layouts/base.html` and override `{% block content %}`.
- Flash messages use categories: `success`, `danger`, `info`.
- New models require: create file in `app/models/`, import in `app/models/__init__.py`, then run `flask db migrate` + `flask db upgrade`.
- New blueprints require: create file in `app/controllers/`, register in `app/__init__.py` `create_app()`.
- New sectors require: create `app/sectors/{sector_name}/prompt.txt` with `{nombre}`, `{descripcion}`, `{ubicacion}` placeholders, and add the sector key to the `LandingForm` choices.
- Authorization on dashboard routes is manual: check `current_user.professional` ownership before modifying Professional/Service records.
