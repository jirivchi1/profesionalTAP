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

Flask MVC app (Spanish UI) — a "TapShare" product that lets professionals create a QR-linked public profile to capture leads. SQLite database via SQLAlchemy.

**App factory** in `app/__init__.py` — `create_app()` initializes extensions and registers blueprints. Extensions (db, migrate, login_manager, csrf) are instantiated in `app/extensions.py` to avoid circular imports.

**Layers:**
- `app/controllers/` — Flask Blueprints. Each file defines a Blueprint registered in `create_app()`. Routes live here, not in models or services.
- `app/models/` — SQLAlchemy models. All models must be imported in `app/models/__init__.py` so Alembic detects them for migrations.
- `app/forms/` — Flask-WTF form classes with validation logic.
- `app/services/` — Business logic (currently empty, use when controllers get complex).
- `app/templates/` — Jinja2 templates. `layouts/base.html` is the shared layout. Subdirectories match blueprint names.

**Blueprints:**
- `public` — home, about, contact, professional listings (`/profesionales`)
- `auth` — login/register
- `dashboard` — profile + services CRUD, QR/contact management, outreach message generator (`/dashboard/mensaje/<id>` → JSON)
- `landing` — TapShare flow: create profile at `/comenzar`, public QR profile at `/p/<slug>`, contact capture at `/p/<slug>/contactar`
- `admin` — analytics + orders list at `/admin`, protected by `admin_required` decorator (checks `User.is_admin`)

**TapShare flow:** A professional fills out `/comenzar` (no login required) → `LandingRequest` row is created with a `public_slug` → QR code generated pointing to `/p/<slug>` → visitors scan the QR and submit a `Contact` record. After creation, `session['pending_request_id']` is set (for post-registration claim). Authenticated users see their QRs and captured contacts in `/dashboard`.

**Key models:**
- `User` — has `is_admin` bool; one-to-one with `Professional`
- `LandingRequest` — the core record: `sector`, `public_slug`, B2B contact fields, `qr_code` (base64 PNG), `landing_type` (`'b2b'`/`'b2c'`). Fields `generated_prompt`/`generated_html` exist in schema but are not populated by the current flow.
- `LandingService` — up to 3 services per `LandingRequest`, ordered by `order` column
- `Contact` — lead captured from a QR scan, linked to a `LandingRequest` and optionally a `LandingService`
- `Professional` / `Service` — legacy profile system, separate from the TapShare QR flow

**Sector themes:** `SECTOR_THEMES` dict in `app/controllers/landing.py` maps sector keys to colors/icons used in templates. Current sectors: `abogatap`, `segurotap`, `inmotap`, `consultortap`. A `saludtap/prompt.txt` file still exists on disk but that sector was removed from the form and themes.

**Auth:** Flask-Login handles sessions. Passwords hashed with `werkzeug.security`. Login-required redirects go to `auth.login`. CSRF protection enabled globally via Flask-WTF's `CSRFProtect`. Admin routes use the `admin_required` decorator (wraps `@login_required` + `is_admin` check).

**Config:** `config.py` reads `SECRET_KEY` and `DATABASE_URL` from env vars with dev defaults. DB file is `app.db` at project root.

## Conventions

- All user-facing text is in **Spanish**.
- Templates extend `layouts/base.html` and override `{% block content %}`.
- Flash messages use categories: `success`, `danger`, `info`.
- New models: create file in `app/models/`, import in `app/models/__init__.py`, run `flask db migrate` + `flask db upgrade`.
- New blueprints: create file in `app/controllers/`, register in `app/__init__.py` `create_app()`.
- New sectors: add key to `SECTOR_THEMES` in `landing.py`, add choice to `LandingForm` in `app/forms/landing.py`, create `app/sectors/{sector_name}/prompt.txt`.
- Authorization on dashboard routes is manual: verify `contact.request.user_id == current_user.id` (or professional ownership) before serving data.
