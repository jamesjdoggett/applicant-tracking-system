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
