# Applicant Tracking System (ATS)

## Problem Statement

Employees need an internal system to keep candidate contact information, job openings, and hiring progress organized. One candidate may apply to multiple openings, and staff need to manage each application independently without creating duplicates. The assignment requires an application that is simple to maintain and easy to explain during a Design Defense.

## Solution

Build a staff-only Django application for managing candidates, openings, and applications. Staff share access to records and use a searchable hiring table to change application stages without full-page reloads. Candidates do not sign in. Candidate archiving preserves existing applications, while explicit deletion rules govern applications and openings.

## User Stories

1. As a staff member, I want to sign in, so that hiring records are accessible only to authorized employees.
2. As an administrator, I want to create staff accounts through Django admin, so that access is centrally managed.
3. As a staff member, I want to create, view, and edit candidate contact information, recruitment source, and general notes, so that recruiting information stays organized.
4. As a staff member, I want email-based duplicate prevention, so that a candidate's applications stay together under one record.
5. As a staff member, I want to search candidates by name or email and filter active or archived records, so that I can find the right person.
6. As a staff member, I want to archive and restore candidates, so that inactive records leave default lists without losing their applications.
7. As a staff member, I want to create, view, and edit openings with descriptions and Open or Closed status, so that hiring opportunities are tracked.
8. As an administrator, I want to manage a shared skills list through Django admin, so that staff can reuse consistent skill names.
9. As a staff member, I want to associate multiple skills with an opening, so that its skill needs are recorded.
10. As a staff member, I want to search openings by title and filter by Open or Closed status, so that I can find relevant positions.
11. As a staff member, I want candidate and opening detail pages to show related applications and management actions, so that I can work from either context.
12. As a staff member, I want to create an application for an existing active candidate and open opening, so that one candidate can be considered for multiple positions.
13. As a staff member, I want duplicate candidate-opening applications blocked, so that each pairing has one application regardless of its stage.
14. As a staff member, I want applications to start at Applied and record their creation date automatically, so that entry is consistent.
15. As a staff member, I want a pipeline table with candidate name/email search and opening and stage filters, so that I can find applications quickly.
16. As a staff member, I want to change stages using an inline dropdown without a full-page reload, so that I can update progress efficiently.
17. As a staff member, I want to skip stages, move backward, and correct terminal stages, so that the system reflects actual hiring activity and mistakes can be corrected.
18. As a staff member, I want closing an opening to prevent new applications while allowing existing applications to progress, so that work already underway can continue.
19. As a staff member, I want reopening an opening to preserve existing stages and permit new applications again, so that hiring can resume without resetting progress.
20. As a staff member, I want to delete an application after confirmation, so that mistaken applications can be removed and recreated correctly.
21. As a staff member, I want to delete an opening only when it has no applications or all applications are terminal, so that ongoing hiring work cannot be removed with the opening.
22. As a staff member, I want opening-deletion confirmation to show the applications being removed, so that I understand the consequences before deleting them together.

## Implementation Decisions

- Required stack: Python, Django, SQLite, uv, Tailwind CSS with DaisyUI through django-tailwind-cli, HTMX, Ruff, and automated testing with pytest and pytest-django.
- Prefer conventional Django models, forms, views, templates, authentication, and admin features. Keep the application small and explainable rather than introducing unnecessary architecture.
- Access: authenticated staff have the same ability to manage all candidates, openings, and applications. Administrators create accounts using Django admin. Candidates have no accounts or access. Enforce access on both full-page views and HTMX endpoints.
- Candidate fields: required name, email, and recruitment source; optional phone, source details, and plain-text internal notes; an archive flag.
- Recruitment source categories are company website, job boards, referrals, and other sources. Optional source details identify a particular board, referrer, or other source.
- Candidate email matching ignores capitalization and surrounding whitespace. Enforce uniqueness consistently when creating and editing records, including archived records.
- Staff may edit candidates whether active or archived. Archived candidates are excluded from default candidate lists but can be found with the archive filter and restored.
- Archiving prevents new applications for that candidate. Existing applications remain visible and manageable, including stage changes. Candidate deletion is not offered in the staff interface.
- Opening fields: required title and description, Open or Closed status, and optional associated skills. Separate openings may have identical titles.
- Skills have unique names and a many-to-many relationship with openings. Administrators maintain skills through Django admin; staff select existing skills using a conventional multiple-selection field on opening forms.
- Applications reference exactly one candidate and one opening, store the current stage, and record creation date automatically. They do not contain notes or stage-change history.
- Application creation selects an existing active candidate and an open opening. Creating a candidate is a separate step. Every new application starts at Applied.
- Enforce one application per candidate-opening pair with a database uniqueness constraint and useful form feedback. Existing Hired, Rejected, or Withdrawn applications still block duplicates. Explicitly deleting an application removes that pairing, permitting a replacement if creation rules are satisfied.
- An application's candidate and opening cannot be edited after creation. Staff correct a mistaken pairing by deleting the application and creating another at Applied.
- Stages are Applied, Screening, Interview, Final Review, Offer, Hired, Rejected, and Withdrawn. Hired, Rejected, and Withdrawn count as terminal stages for opening-deletion eligibility.
- Stage-rules prototype decision: adopt policy A, flexible changes. Any stage may change directly to any other stage, including backward moves, skips, and changes out of terminal stages. No separate correction mode is required. The rationale is simplicity for trusted staff.
- Opening closure prevents new applications but does not freeze existing ones. Existing applications can change to any stage while an opening is Closed. Closing and reopening never change stages automatically; reopening permits new applications again for active candidates without an existing pairing.
- Pipeline interface prototype decision: adopt variant A, the filterable table, because it is compact and straightforward to implement with Django templates and HTMX. Rows show candidate name/email, opening, current stage, and creation date. Provide candidate name/email search, an opening filter, and a stage filter.
- Inline stage dropdowns save through HTMX, update the relevant page fragment without a full-page reload, and provide visible feedback. Updates must keep the displayed table consistent with its active filters, including when a changed stage no longer matches the selected stage filter.
- Candidate and opening browsing uses conventional searchable, paginated lists and detail pages. Candidates support name/email search and Active/Archived filtering; openings support title search and Open/Closed filtering. Detail pages show related applications and appropriate management actions.
- Staff may delete individual applications from any stage after confirmation. No terminal-stage restriction was adopted for individual application deletion.
- Staff may delete an opening only when it has no applications or every associated application is Hired, Rejected, or Withdrawn. Opening status itself is not an additional deletion condition.
- Eligible opening deletion cascades to all its applications and preserves candidate records. A confirmation page shows the applications that will be deleted. Enforce eligibility on the server at deletion time, not solely when displaying the confirmation page.
- Use ordinary confirmation pages and protected POST actions for destructive operations, following Django's standard CSRF protection.
- Verification should cover meaningful behavior: staff access, normalized candidate email uniqueness, candidate archiving and restoration, application creation restrictions and database uniqueness, immutable application pairing, flexible stage changes including closed openings and terminal states, HTMX responses, search/filter behavior, and deletion eligibility and cascade effects. Use Ruff for linting and formatting checks.

## Out of Scope

- Candidate login, public applications, self-registration, and candidate-facing pages.
- Separate staff viewer/editor roles, opening assignments, or record-level ownership permissions.
- Résumé uploads or other file attachments.
- Candidate merging or shared email addresses across candidate records.
- Permanent candidate deletion through the staff interface.
- Department, location, employment type, and salary fields on openings.
- Staff-facing skill-management pages or inline skill creation.
- Creating a candidate inside the application form or selecting an initial stage other than Applied.
- Application notes, interview feedback records, stage audit history, and dedicated correction workflows.
- Board or list/detail pipeline layouts, drag-and-drop interactions, advanced filtering by source/skills/dates, or additional sorting features.
- Automatic stage changes when openings close or reopen, or strict sequential stage progression.
- Additional features such as messaging, calendar scheduling, reporting dashboards, bulk operations, external integrations, and deployment infrastructure.

## Further Notes

- Both required prototypes were completed and reviewed: flexible application-stage rules and three structurally different hiring-pipeline interfaces. The user selected policy A for the rules and variant A for the interface.
- Prototype behavior and styling are exploratory. Implement the selected behavior in the required Django stack rather than promoting standalone prototype JavaScript or CDN setup into production.
- The stage-rules prototype's action log is an explanation aid, not a requirement for production audit history.
- The repository currently contains project documentation and standalone prototypes, with no Django application implemented. This PRD authorizes no implementation by itself; it records the completed requirements interview.
- Keep later implementation and its explanation focused on assignment requirements and Design Defense clarity.
