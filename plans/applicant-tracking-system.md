# Plan: Applicant Tracking System

> Source PRD: [Completed Applicant Tracking System PRD](../prd/applicant-tracking-system.md)
>
> Status: Approved on 2026-10-31. The ten-phase breakdown is final. All ten phases passed automated checks and received user approval after browser-verification instructions.

## Architectural decisions

- **Stack**: Python, Django, SQLite, uv, Tailwind CSS and DaisyUI through django-tailwind-cli, HTMX, Ruff, pytest, and pytest-django. Use conventional Django models, forms, views, templates, authentication, and admin; no service framework or API layer is needed.
- **Owning app**: One Django app, `recruiting`, owns candidates, skills, openings, and applications. Use Django's existing user model and authentication.
- **URLs**: Named, app-namespaced routes under `/candidates/`, `/openings/`, and `/applications/`; use integer primary keys for record URLs. `/applications/` is the pipeline. Use `/accounts/login/`, `/accounts/logout/`, and `/admin/` for authentication and administration. Nest record actions under their record URL, including `/applications/<pk>/stage/`. Use query parameters for search, filters, and pagination.
- **Models**: `Candidate` stores the PRD contact/source fields and archive flag; `Opening` stores title, description, and Open/Closed status; `Skill` has a unique name and an M2M relationship with `Opening`; `Application` has candidate/opening foreign keys, stage, and automatic creation date. Introduce each model and migration in its first usable slice.
- **Constraints**: Store candidate emails trimmed and lowercase, enforce uniqueness including archived candidates, and normalize on all supported write paths, including admin. Enforce candidate-opening uniqueness in the database as well as providing form feedback. Application pairings remain immutable. Opening deletion cascades to applications and preserves candidates; no staff candidate-deletion interface is offered.
- **Access and mutations**: All recruiting pages and HTMX endpoints require authenticated staff. Staff share access to all records. Administrators manage staff and skills through Django admin. Use CSRF-protected POST actions for mutations and ordinary confirmation pages for deletion.
- **Stage policy**: Use the eight PRD stages. Every stage can change directly to every other stage. Hired, Rejected, and Withdrawn are terminal only for opening-deletion eligibility. Archived candidates and closed openings retain fully manageable existing applications.
- **Interface**: Use server-rendered pages and conventional Django forms. Apply simple, consistent Tailwind/DaisyUI styling as each screen is introduced. HTMX is limited to inline stage changes and their filtered-table response. Do not reuse prototype JavaScript or CDN setup as production code.

## Working and verification rules

- Each phase is intended for one coding session and delivers a complete, usable path. Include the necessary models, migrations, forms, views, templates, styling, and tests in that phase; do not create separate layer-only phases.
- Use pytest and pytest-django for meaningful behavior tests, including authenticated staff, anonymous users, and authenticated non-staff users on newly introduced endpoints. Test POST-only mutation and CSRF behavior where relevant.
- At each phase, run its behavior tests and the accumulated regression suite, Django system checks, Ruff lint and formatting checks, and migration consistency checks. Apply migrations to a local SQLite database and verify the manual scenario listed below. Record results and any remaining issues.
- Use normal Django form validation and database constraints. Recheck eligibility server-side when accepting mutations; filtered form choices and hidden UI controls alone are insufficient.
- Story references can span phases when a story has distinct creation, browsing, and application-management behaviors. Later phases extend earlier slices without requiring unfinished pages or broken links.
- Respect all PRD exclusions. Do not add uploads, candidate accounts, audit history, dashboards, extra roles, or deployment infrastructure.

---

## Phase 1: Staff sign-in and account administration

**User stories**: 1, 2.

### What to build

Bootstrap the required Django/uv stack, SQLite configuration, Tailwind/DaisyUI build, Ruff, and pytest-django. Deliver a styled staff sign-in/sign-out flow and a minimal protected landing page. Administrators can create staff accounts in Django admin. Establish shared navigation and staff access enforcement for later pages; configure HTMX for later use without building pipeline behavior yet.

### Acceptance criteria

- [x] An administrator can create a staff account; that account can sign in, reach the protected page, and sign out using POST.
- [x] Anonymous users must sign in, and authenticated non-staff users cannot access recruiting pages. Do not introduce self-registration.
- [x] Automated tests cover these access paths and sign-in/sign-out behavior using pytest and pytest-django; the required CSS build and Ruff checks work.
- [x] Manual: create an account through admin, sign in and out, and inspect the styled page and login errors. User approved Phase 1 after receiving the browser-verification steps.

---

## Phase 2: Candidate creation, details, and editing

**User stories**: 3, 4; initial list support for 5.

### What to build

Introduce `Candidate` and its migration. Deliver a basic paginated active-candidate list with create, detail, and edit pages. Include required name, email, and recruitment source; optional phone, source details, and plain-text notes; and the four approved source categories. Normalize email consistently and return useful duplicate feedback on creation and editing. Related applications arrive in phase 6.

### Acceptance criteria

- [x] Staff can create, view, and edit all approved candidate fields; required fields and source choices are validated, and notes render as escaped plain text.
- [x] Email matching ignores surrounding whitespace and capitalization; duplicates are rejected on creation and editing, including collisions with archived records. An unchanged email remains valid on edit.
- [x] Automated tests cover field validation, normalized email storage and uniqueness, supported admin writes, pagination, and staff access.
- [x] Manual: create and edit a candidate, then attempt a duplicate with different case and surrounding spaces. User approved Phase 2 after receiving the browser-verification steps.

---

## Phase 3: Candidate search, archiving, and restoration

**User stories**: 5, 6; archived-record editing from 3.

### What to build

Add name/email search, Active/Archived filtering, and POST archive/restore actions. Preserve search/filter selections across pagination. Default lists show active candidates, while archived candidates retain accessible detail/edit pages and a restore action. Application-preservation behavior is verified when applications are introduced in phase 6.

### Acceptance criteria

- [x] Staff can search by name or email and filter Active/Archived records; pagination preserves the current query.
- [x] Archiving removes a candidate from the default list; restoration returns it. Staff can edit archived records without bypassing duplicate-email prevention.
- [x] Automated tests cover search/filter combinations, pagination state, archive/restore mutations, editing archived records, and access control. Candidate deletion is absent from the staff interface.
- [x] Manual: archive a candidate, find and edit it using the Archived filter, then restore it. User approved Phase 3 after receiving the browser-verification steps.

---

## Phase 4: Openings and shared skills

**User stories**: 7, 8, 9.

### What to build

Introduce `Opening`, `Skill`, their relationship, and migrations. Deliver a basic paginated opening list and create/detail/edit pages with required title and description, Open/Closed status, and an optional conventional multiple-selection field for existing skills. Administrators maintain unique skill names in Django admin; staff have no skill-creation interface.

### Acceptance criteria

- [x] Staff can create, view, and edit openings, including status and multiple skills; separate openings may share a title.
- [x] Administrators can manage the shared skills list, duplicate skill names are rejected, and openings can have no skills.
- [x] Automated tests cover required fields, status choices, M2M persistence and editing, duplicate titles, skill uniqueness, and access control.
- [x] Manual: create skills in admin, create an opening with several skills, then edit its status and skill selection. User approved Phase 4 after receiving the browser-verification steps.

---

## Phase 5: Opening search and status filtering

**User stories**: 10; browsing portion of 7.

### What to build

Extend the opening list with title search and Open/Closed filtering. Preserve query state across pagination and provide clear empty results. Keep this session narrow; application effects of closing and reopening belong to phase 6.

### Acceptance criteria

- [x] Search and status filters work separately and together, including openings with identical titles.
- [x] Pagination retains search and status selections, and empty results have a usable route back to broader results.
- [x] Automated tests cover combined filters, pagination, empty results, and staff access.
- [x] Manual: create enough openings to paginate, search by title, switch statuses, and verify navigation retains the selection. User approved Phase 5 after receiving the browser-verification steps.

---

## Phase 6: Application creation from candidate and opening contexts

**User stories**: 11–14, 18, 19; application preservation from 6. Related deletion actions arrive in phases 9–10.

### What to build

Introduce `Application` and its database pairing constraint. Deliver application creation using existing active candidates and open openings; every application starts at Applied and records its creation date automatically. Candidate and opening details list related applications and provide creation actions when eligible. Reuse the same creation flow from either context. Recheck eligibility on submission and keep pairing fields immutable after creation. Provide useful duplicate feedback, including for existing terminal applications.

### Acceptance criteria

- [x] One candidate can apply to multiple openings, and an opening can receive multiple candidates. Duplicate pairings are rejected by forms and the database at every stage.
- [x] Archived candidates and closed openings cannot receive new applications, including a form submitted after either status changes. Reopening permits new eligible pairings.
- [x] Creation always uses Applied and an automatic date; submitted stage/date overrides are not accepted. No application-pairing edit action exists.
- [x] Candidate archiving and opening closure/reopening preserve related applications and their stored stages; related records remain visible from both detail pages.
- [x] Automated tests cover creation, defaults, forged input, immutable pairings, uniqueness including terminal records, eligibility changes, detail relationships, and staff access.
- [x] Manual: create applications from both detail contexts, try a duplicate, archive/restore a candidate, and close/reopen an opening while checking preserved applications. User approved Phase 6 after receiving the browser-verification steps.

---

## Phase 7: Searchable and filterable pipeline table

**User stories**: 15; table presentation supporting 16.

### What to build

Deliver `/applications/` as the selected table interface with candidate name/email, opening, current stage, and creation date. Add candidate name/email search plus opening and stage filters that work together. Show existing applications for archived candidates and closed openings. Link records to their existing detail pages. Inline stage editing follows in phase 8.

### Acceptance criteria

- [x] All required columns are visible, and each search/filter combination returns the correct applications.
- [x] Archived candidates and closed openings retain visible applications; empty results provide useful feedback.
- [x] Automated tests cover candidate name/email search, both filters individually and together, row contents, retained archived/closed records, and access control.
- [x] Manual: find applications using search and each filter, combine all three, and open their candidate/opening details. User approved Phase 7 after receiving the browser-verification steps.

---

## Phase 8: Inline stage changes with HTMX

**User stories**: 16, 17; stage-management portions of 6, 18, 19.

### What to build

Add inline stage dropdowns and a protected HTMX POST endpoint. Permit every valid stage-to-stage transition, including skips, backward moves, and changes out of terminal stages. Keep existing applications editable for archived candidates and closed openings. Render the affected table fragment using the active search and filters; remove a changed row if it no longer matches and show clear success or error feedback.

### Acceptance criteria

- [x] Dropdown changes persist without full-page reloads and visibly report success or validation failure; invalid stages do not alter stored data.
- [x] Changes work across all eight stages, including terminal-to-active changes, archived candidates, and closed openings. Closing/reopening never changes stages automatically.
- [x] The returned fragment reflects current filters, including an empty-result message when the last matching row leaves the selected stage.
- [x] Automated tests cover the transition matrix, HTMX fragment responses, filter consistency, invalid input, staff access, POST-only behavior, and CSRF protection. Pairing fields cannot be changed through this endpoint.
- [x] Manual: change stages forward and backward, leave a terminal stage, then change the last row under a stage filter and verify feedback and row removal without a reload. User approved Phase 8 after receiving browser-verification steps and clearer Applications navigation.

---

## Phase 9: Confirmed application deletion

**User stories**: 20; application management actions from 11 and pairing correction from 13.

### What to build

Add application-deletion links from the pipeline and related application lists. Use a confirmation page identifying the candidate and opening and a protected POST to delete. Allow deletion at every stage, including for archived candidates and closed openings. After deletion, the pairing may be recreated only if normal creation rules are satisfied, starting again at Applied.

### Acceptance criteria

- [x] Viewing or cancelling confirmation changes nothing; confirmed POST removes only the selected application and preserves both parent records.
- [x] Every stage can be deleted. Recreating a deleted pairing succeeds for an active candidate/open opening and remains blocked otherwise.
- [x] Automated tests cover confirmation, cancellation, deletion across stages, parent preservation, replacement at Applied, POST/CSRF restrictions, and staff access.
- [x] Manual: cancel a deletion, confirm it, and recreate the eligible pairing with its initial stage. User approved Phase 9 after receiving browser-verification steps.

---

## Phase 10: Guarded opening deletion

**User stories**: 21, 22; opening management actions from 11.

### What to build

Add opening deletion with a confirmation page showing all applications that will be removed. Permit deletion when there are no applications or every application is Hired, Rejected, or Withdrawn, regardless of opening status. Recheck eligibility when processing the protected POST so a stage change after confirmation can prevent deletion. Delete eligible openings and their applications together, preserving candidates.

### Acceptance criteria

- [x] Empty openings and openings with only terminal applications can be deleted whether Open or Closed; any nonterminal application blocks deletion.
- [x] Confirmation identifies the opening and all affected applications. GET and cancellation leave records intact, and a newly nonterminal application blocks a previously eligible confirmation submission.
- [x] Successful deletion removes the opening and its applications while retaining candidates and shared skills.
- [x] Automated tests cover every stage's eligibility, mixed stages, both opening statuses, submission-time rechecks, confirmation contents, cascade effects, POST/CSRF restrictions, and staff access. All 397 tests, Ruff lint/format, Django checks, migration consistency, and CSS build pass.
- [x] Manual: try deletion with an active application, make all applications terminal and inspect confirmation, change one back before submitting to verify rejection, then complete an eligible deletion. User approved Phase 10 after receiving browser-verification instructions.

## Workload and coverage review

- Ten phases are deliberate: the initial setup is paired only with authentication, candidate browsing is separate from entry, and opening browsing is separate from skill-backed forms.
- Phase 6 has more story references because several stories describe the same application-creation rules. Its scope stops at creation and related-record display; pipeline filtering, inline updates, and deletion each receive their own session.
- Phase 8 focuses only on stage updates and filtered HTMX rendering. Phase 10 focuses only on guarded cascading deletion. These are the main behavior-heavy sessions and should not be merged with adjacent phases.
- Every PRD story (1–22) is mapped above. Every phase includes automated verification and a manual demonstration; there is no deferred testing or styling phase.
- Review checkpoint completed: the user approved the ten-phase breakdown on 2026-10-31.
