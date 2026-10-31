# Applicant Tracking System

Internal staff-only Django application for managing candidates, openings, and applications.

## Approved references

- Requirements and scope: [PRD](prd/applicant-tracking-system.md).
- Approved work breakdown: [implementation plan](plans/applicant-tracking-system.md).
- Stage decision reference: [stage-rules prototype](prototypes/application-stage-rules.html); see the PRD for the approved policy.
- Interface decision reference: [pipeline prototype](prototypes/hiring-pipeline.html); see the PRD for the approved selection.
- Prototypes are exploratory references; implement approved behavior in the required Django stack.

## Technology stack

- Language, framework, and database: Python, Django, SQLite.
- Package manager: uv.
- Styling: Tailwind CSS with DaisyUI through django-tailwind-cli.
- Interactions: HTMX with Django-rendered HTML fragments.
- Automated testing: pytest and pytest-django.
- Linting and formatting: Ruff.

## Project-wide guidance

- Use conventional Django models, forms, views, templates, authentication, and admin.
- Enforce authenticated staff access on full-page views and HTMX endpoints.
- Use Django admin for centralized account administration.
- Follow Django's standard CSRF protection and protected POST actions for destructive operations.
- Keep architecture small, maintainable, and explainable for the Design Defense.
- Follow the approved PRD scope and plan; verify meaningful behavior with automated and manual testing.
- Layout: `config/` holds Django configuration; `recruiting/` holds app code, templates, and pytest tests.
- Dependencies: `uv sync --locked` installs the versions recorded in `uv.lock`.
- Checks: `uv run pytest`, `uv run ruff check .`, and `uv run ruff format --check .`.
- CSS: edit `styles/app.css`; build with `uv run python -X utf8 manage.py tailwind build`; static assets live in `static/`.
- Protect recruiting views with `recruiting.decorators.staff_required`; reuse the shared `base.html` template.
- Candidate staff forms and `CandidateAdmin` share `recruiting.forms.CandidateForm`; keep validation shared.
- `Candidate.save()` normalizes email; bulk writes bypass it and are not a supported candidate write path.
- Django checks: `uv run python manage.py check` and `uv run python manage.py makemigrations --check --dry-run`.
- List filters use GET forms with `q` and `status`; trim search input, validate status values, and preserve normalized selections in pagination links with Django's `{% querystring %}` tag.
- Archive/restore actions use explicit target states and `save(update_fields=["is_archived"])` so repeated submissions are safe.
- Opening forms use `ModelForm.save()` to persist skills; if using `commit=False`, call `save_m2m()` after saving the instance.
- Application creation uses `ApplicationForm` with fresh eligible-record querysets on each request; query parameters preselect records, while validated POST fields determine the new pairing.
- Related application lists use `select_related()` for the opposite parent to avoid per-row queries.
- Pipeline queries use `select_related("candidate", "opening")`; GET filters are `q`, `opening` (record ID), and `stage`, with invalid filter values normalized to all records.
- Opening labels in the pipeline include record IDs to distinguish identical titles.
