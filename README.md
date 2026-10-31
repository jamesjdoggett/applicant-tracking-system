# Applicant Tracking System

CIDM 3312 Project #1: an internal staff-only Django application.

Phase 1 provides staff sign-in/sign-out, a protected landing page, and account
administration through Django admin. Browser verification was approved by the user.

## Local setup

Install uv and Python 3.14, then run these commands from the repository root:

```powershell
uv sync --locked
uv run python manage.py migrate
uv run python -X utf8 manage.py tailwind build
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Open http://127.0.0.1:8000/. The checked-in Django settings are for local development.
SQLite data, generated CSS, and the downloaded Tailwind CLI are ignored by Git.
The first CSS build downloads the pinned DaisyUI-enabled CLI. HTMX 2.0.10 is
vendored with its license and served locally; no CDN or Node.js setup is needed.

To rebuild CSS automatically while editing templates, use this server command:

```powershell
uv run python -X utf8 manage.py tailwind runserver
```

The UTF-8 option allows the Tailwind command's status symbols to print correctly
in Windows terminals.

## Staff accounts

1. Sign in at http://127.0.0.1:8000/admin/ using your superuser account.
2. Under Users, choose Add, enter a username and password, and save.
3. On the user's edit page, enable **Staff status**, leave **Active** enabled, and
   save. Ordinary staff need no additional permissions to access the application.
4. Sign out, then use the new account at http://127.0.0.1:8000/accounts/login/.

Superusers manage accounts through admin. Staff without user-management
permissions cannot create accounts. Sign-out uses a CSRF-protected POST form.

## Verification

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python -X utf8 manage.py tailwind build
```

Tests cover staff-only access for ordinary and HTMX requests, sign-in errors,
redirects, POST/CSRF-protected sign-out, and staff account creation through admin.

## Approved references

- [PRD](prd/applicant-tracking-system.md)
- [Implementation plan](plans/applicant-tracking-system.md)
- [Stage-rules prototype](prototypes/application-stage-rules.html)
- [Pipeline prototype](prototypes/hiring-pipeline.html)
