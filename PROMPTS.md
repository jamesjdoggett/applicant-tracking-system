## 2026-10-31 — Phase 9 confirmed application deletion

### Prompts

1. Supplied AGENTS.md project instructions and the Windows workspace context.
2. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 9 only.`
3. Supplied the implement skill, including TDD approval checkpoints, full feedback checks, browser verification with confirmation, and final logging, commit, and push.
4. Answered `yes` to selecting confirmed deletion that removes only the selected application while preserving parents and other applications for TDD.
5. Answered `yes` to the RED checkpoint after the selected application still existed following POST.
6. Answered `approved` to the GREEN checkpoint after all 42 application tests passed.
7. Approved Phase 9 after receiving browser-verification instructions. Requested a concise AGENTS.md review with no more than five added lines per phase and a final target of 60–80 lines maximum after ten phases; accurate Phase 9 logging; review and staging of all Phase 9 changes; the exact commit message `Phase 9 Complete`; and a GitHub push with success confirmation. Explicitly prohibited starting Phase 10.

### Summary

- **Outcome:** Implemented Phase 9 only: deletion links in the pipeline and both related application lists, a confirmation page identifying candidate/email, opening/ID, and stage, and staff-only CSRF-protected POST deletion. GET and cancellation preserve records; deletion preserves parents and other applications. Tests cover all eight stages with active/archived candidates and open/closed openings, eligible replacement at Applied with a new identity/date, blocked ineligible replacement, access control including HTMX requests, unsupported methods, missing records, and CSRF enforcement. All 363 tests passed; Ruff lint/format, Django system and migration consistency checks, local migration application, and the production CSS build passed. The local database required no migrations. User approved Phase 9 after browser-verification instructions. Added one durable convention to AGENTS.md and marked Phase 9 approved in the plan. Finalization uses the requested commit message; the commit hash and verified push result are reported after Git verification.
- **Deviations:** No scope changes. Paused at every required TDD and manual-verification checkpoint. No Phase 10 work started.
- **Sideways:** An exploratory read referenced a nonexistent recruiting/conftest.py; existing fixtures were in test_applications.py. Sandbox permissions blocked uv cache access and the Tailwind binary; approved escalation allowed both. The RED test failed on its intended assertion before implementation. Pytest initially warned about optional cache writes; subsequent runs disabled the cache provider. Removed an unnecessary assertion during review, reran its test and Ruff checks, and confirmed they passed.

# PROMPTS.md — AI Usage Log

## 2026-10-31 — Phase 8 inline stage changes with HTMX

### Prompts

1. Supplied AGENTS.md project instructions and the Windows workspace context.
2. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 8 only.`
3. Supplied the implement skill: follow the approved documents and TDD approval checkpoints, run feedback loops, provide browser-verification steps and wait for confirmation, then update this log, commit, and push.
4. Answered `yes` to selecting flexible stage transitions and filtered HTMX updates for TDD.
5. Answered `yes` to the transition RED checkpoint: posting Applied for a Screening application returned HTTP 200 but left its stage unchanged; approved the test of all 64 transitions under active/open and archived/closed conditions.
6. Answered `approved` to the transition GREEN review after all 178 pipeline/application tests passed.
7. Answered `yes` to the filtered HTMX RED checkpoint: the stage saved but the response lacked success feedback and returned a full page; approved requiring the current filters, a results fragment, and empty-result feedback when the sole matching row leaves the selected stage.
8. Answered `approved` to the filtered HTMX GREEN review after all 179 pipeline/application tests passed.
9. Reported: `I do not see "Applications" on the home page. Please ensure the feature has been added and specify where to find it on the webpage.`
10. Approved Phase 8. Requested review of AGENTS.md with only important verified commands, project structure, and durable architectural conventions; no more than five added lines per phase and a final target of 60–80 lines maximum after ten phases; accurate Phase 8 logging here; review and staging of all Phase 8 changes; the exact commit message `Phase 8 Complete`; and a GitHub push with success confirmation. Explicitly prohibited starting Phase 9.

### Summary

- **Outcome:** Implemented Phase 8 only: inline stage dropdowns with CSRF-protected staff-only POST updates; validation accepting all eight stages with only the stage field saved; all 64 transitions supported for active/open and archived/closed records; shared pipeline filter context and results fragment; HTMX replacement of the table, result count, success/error feedback, and empty-result message while retaining active search/opening/stage filters. Invalid stages preserve stored data, and forged pairing/date fields are ignored. Renamed navigation to Applications and the home link to View applications after the user's discoverability feedback. All 320 tests passed, including the transition matrix, filtered fragments, invalid input, immutable pairing/date, access control, POST-only methods, CSRF, and missing records. Ruff lint/format, Django system checks, migration consistency, and CSS build passed; no migrations were pending. User approved Phase 8 after receiving browser-verification instructions. Added two durable conventions to AGENTS.md and marked Phase 8 approved in the plan. Finalization uses the requested commit message; commit hash and push result are reported after Git verification.
- **Deviations:** No changes to approved Phase 8 scope. Paused at the TDD selection, both RED/GREEN reviews, and manual-verification checkpoint. Clarified Applications labels at the user's request. No Phase 9 work was started.
- **Sideways:** Initial reads assumed tests were in a tests directory; located the existing recruiting/test_pipeline.py. Sandbox restrictions blocked uv cache access, so checks were rerun with approved escalation. Both selected TDD tests failed on intended assertions before implementation made them pass. Initial pytest cache-write warnings were avoided in subsequent runs with the optional cache provider disabled. Updated the existing home-link assertion for the clarified label. Final checks have no unresolved failures.

## 2026-10-31 — Phase 7 searchable and filterable pipeline

### Prompts

1. Supplied AGENTS.md project instructions and the Windows workspace context.
2. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 7 only.`
3. Supplied the implement skill: follow the approved documents and TDD approval checkpoints, run feedback loops, provide browser-verification steps and wait for confirmation, then update this log, commit, and push.
4. Answered `yes` to selecting the intersection of candidate search, opening, and stage filters for TDD.
5. Answered `yes` to the RED checkpoint: the pipeline returned all four applications rather than the one matching the trimmed, case-insensitive email search and both filters.
6. Answered `approved` to the GREEN review after the selected test and all 42 pipeline/application tests passed.
7. Approved Phase 7 after receiving browser-verification instructions. Requested review of AGENTS.md with only important verified commands, project structure, and durable conventions; no more than five added lines per phase and a final target of 60–80 lines maximum after ten phases; accurate Phase 7 logging here; review and staging of all Phase 7 changes; the exact commit message `Phase 7 Complete`; and a GitHub push with success confirmation. Explicitly prohibited starting Phase 8.

### Summary

- **Outcome:** Implemented Phase 7 only: staff-only `/applications/` pipeline with candidate name/email, opening, stage, and creation date; candidate and opening detail links; combined candidate name/email search and opening/stage filters; normalized selections; useful empty-result/reset feedback; navigation and home links; and retained applications for archived candidates and closed openings. Opening labels include IDs to distinguish duplicate titles, and related records are loaded with select_related. All 175 tests passed. Ruff lint/format, Django system checks, migration consistency, and the CSS build passed; the local database had no pending migrations. User approved Phase 7 after browser-verification instructions. Added two durable lines to AGENTS.md and marked Phase 7 approved in the plan. Finalization uses the requested commit message; the commit hash and verified push result are reported after Git verification.
- **Deviations:** No changes to approved Phase 7 scope. Paused at the TDD selection, RED/GREEN reviews, and manual-verification checkpoint. No Phase 8 work was started.
- **Sideways:** Sandbox restrictions blocked uv cache access; reran checks with approved escalation. The selected test failed on its intended assertion before filtering made it pass. Pytest reported an optional cache-write warning; all tests passed. Ruff formatted the new test file. No unresolved check failures remain.

## 2026-10-31 — Phase 6 application creation and related records

### Prompts

1. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 6 only.`
2. Supplied the implement skill: follow the PRD and plan, use the TDD skill with required approvals, run feedback loops, provide browser-verification steps and wait for confirmation, then update this log, commit, and push.
3. Answered `yes` to selecting duplicate-pairing prevention across all stages and submission-time candidate/opening eligibility for TDD.
4. Answered `yes` to the duplicate-pairing RED checkpoint: the form accepted an existing Applied pairing; approved the test requiring useful form feedback and database rejection at all eight stages.
5. Answered `approved` to the duplicate-pairing GREEN review after all 126 tests passed.
6. Answered `yes` to the eligibility RED checkpoint: submitting after candidate archiving created an application instead of returning a field error; approved the test also covering opening closure and successful creation after restoration/reopening.
7. Answered `approved` to the eligibility GREEN review after all 127 tests passed.
8. Approved Phase 6 after receiving browser-verification instructions. Requested review of AGENTS.md with only important verified commands, project structure, and durable conventions; no more than five added lines per phase and a final target of 60–80 lines maximum after ten phases; accurate Phase 6 logging here; review and staging of all Phase 6 changes; the exact commit message `Phase 6 Complete`; and a GitHub push with success confirmation. Explicitly prohibited starting Phase 7.

### Summary

- **Outcome:** Implemented Phase 6 only: Application model and migrations with eight stages, Applied default, automatic creation timestamp, and database candidate-opening uniqueness; a shared staff-only creation form with fresh active-candidate/open-opening choices and descriptive labels; creation links and related application tables on candidate/opening details; context preselection and return navigation; duplicate feedback, including terminal pairings; and preserved applications across candidate archiving/restoration and opening closure/reopening. Pairings have no edit endpoint; creation accepts only candidate/opening fields and ignores stage/date/ID overrides. All 166 tests passed, covering both contexts, defaults, forged/invalid input, multiple applications per parent, form/database uniqueness at every stage, stale-form eligibility, retained relationships/stages/dates, ordinary/HTMX staff access, CSRF, HTTP methods, and invalid contexts. Ruff lint/format, Django system checks, migration consistency, and the CSS build passed; both local Application migrations were applied. User approved Phase 6 after browser-verification instructions. Added two durable conventions to AGENTS.md and marked Phase 6 approved in the plan. Finalization uses the requested commit message; the commit hash and verified push result are reported after Git verification.
- **Deviations:** No changes to Phase 6 scope. Paused for the TDD selection, both RED/GREEN reviews, and manual-verification approval. Pipeline, inline stage editing, and deletion remain in their planned later phases. No Phase 7 work was started.
- **Sideways:** Both selected TDD tests failed on their intended assertions before implementation. The database uniqueness constraint and fresh ModelChoiceField querysets made them pass. Commands used approved escalation for uv cache access. Ruff found one overlong error-message string; split the string and reran lint/format checks successfully. No unresolved check failures remain.

## 2026-10-31 — Phase 5 opening search and status filtering

### Prompts

1. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 5 only.`
2. Supplied the implement skill: follow the PRD and plan, use the TDD skill with required approvals, run feedback loops, provide browser-verification steps and wait for confirmation, then update this log, commit, and push.
3. Answered `yes` to selecting no TDD candidates because the existing tested candidate list already established the search/filter/pagination interface; approved following that pattern with automated opening coverage.
4. Approved Phase 5 after receiving browser-verification instructions. Requested review of AGENTS.md with only important verified commands, project structure, and durable conventions; no more than five added lines per phase and a final target of 60–80 lines maximum after ten phases; accurate Phase 5 logging here; review and staging of all Phase 5 changes; the exact commit message `Phase 5 Complete`; and a GitHub push with success confirmation. Explicitly prohibited starting Phase 6.

### Summary

- **Outcome:** Implemented Phase 5 only: trimmed case-insensitive title search; All/Open/Closed filtering with both statuses visible by default; combined filters including duplicate titles; GET controls and reset link; query-preserving pagination; and useful empty-result guidance. All 125 tests passed, including combined filters, title-only search, pagination state with special characters, empty results/reset, invalid status fallback, and ordinary/HTMX staff access. Ruff lint/format, Django system checks, migration consistency, and the CSS build passed. The local database needed no new migrations. User approved Phase 5 after browser-verification instructions. Refined the existing AGENTS.md filter convention without adding lines and marked Phase 5 approved in the plan. Finalization uses the requested commit message; the commit hash and verified push result are reported after Git verification.
- **Deviations:** No changes to Phase 5 scope. No TDD cycles were needed under the skill's existing-tested-pattern rule; user approved that selection before implementation. Paused for manual-verification approval. No Phase 6 work was started.
- **Sideways:** The new combined-filter test initially expected Developer before Designer; corrected its expected alphabetical order to match existing model ordering, then reran the full suite successfully. Pytest emitted optional cache-write warnings on the initial run; the successful final run disabled the optional cache provider. Commands used approved escalation for uv cache access. No unresolved check failures remain.

## 2026-10-31 — Phase 4 openings and shared skills

### Prompts

1. Supplied AGENTS.md project instructions and the Windows workspace context.
2. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 4 only.`
3. Supplied the implement skill: follow the PRD and plan, use the TDD skill with required approvals, run feedback loops, provide browser-verification steps and wait for confirmation, then update this log, commit, and push.
4. Answered `yes` to selecting opening skill persistence, replacement, and clearing for TDD.
5. Answered `approved` to the RED checkpoint: the opening saved but its selected skills were missing; approved the test covering creation with multiple skills, replacement on edit, and clearing the selection.
6. Answered `approved` to the GREEN review after the selected test and existing regression tests passed (82 total).
7. Approved Phase 4 after receiving browser-verification instructions. Requested review of AGENTS.md with only important verified commands, project structure, and durable conventions; no more than five added lines per phase and a final target of 60–80 lines maximum after ten phases; accurate Phase 4 logging here; review and staging of all Phase 4 changes; the exact commit message `Phase 4 Complete`; and a GitHub push with success confirmation. Explicitly prohibited starting Phase 5.

### Summary

- **Outcome:** Implemented Phase 4 only: Opening and Skill models and migration; unique skill names; optional many-to-many skills; staff-only opening create/detail/edit pages and a stable paginated list; required title/description and validated Open/Closed status; conventional multiple-selection input with selection guidance; admin skill management; and shared navigation. All 118 tests passed, covering required fields, invalid choices, skill persistence/replacement/clearing, duplicate titles, database and admin skill uniqueness, admin editing/deletion, escaped descriptions, pagination, ordinary/HTMX access control, CSRF, allowed methods, and missing records. Ruff lint/format, Django system checks, migration consistency, and the CSS build passed. Applied the migration locally. User approved Phase 4 after browser-verification instructions. Added one durable ModelForm/M2M convention to AGENTS.md and marked Phase 4 approved in the plan. Finalization uses the requested commit message; the commit hash and verified push result are reported after Git verification.
- **Deviations:** No changes to Phase 4 scope. Paused at the required TDD selection, RED, GREEN, and manual-verification checkpoints. No Phase 5 search or status filtering was started.
- **Sideways:** Sandbox restrictions blocked uv cache access; reran commands with approved escalation. The selected TDD test failed on the expected missing-skills assertion; using ModelForm.save() persisted the relationship and made the test pass. Pytest emitted an optional cache-write warning while all tests passed. Ruff formatted four files; final lint and formatting checks passed.

## 2026-10-31 — Phase 3 candidate search, archiving, and restoration

### Prompts

1. Supplied AGENTS.md project instructions and the Windows workspace context.
2. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 3 only.`
3. Supplied the implement skill: follow the PRD and plan, use the TDD skill with required approvals, run feedback loops, provide browser-verification steps and wait for confirmation, then update this log, commit, and push.
4. Answered `yes` to selecting combined candidate search/status filtering and archive/restore behavior for TDD.
5. Answered `yes` to the search/filter RED checkpoint: searching for ALEX also returned an unrelated active candidate; approved the test covering trimmed case-insensitive name/email search combined with archive status and unmatched queries.
6. Answered `approved` to the search/filter GREEN review after all 43 candidate tests passed.
7. Answered `yes` to the archive/restore RED checkpoint: the archive POST left is_archived false; approved the test covering status changes, list visibility, detail access, restoration, and record preservation.
8. Answered `approved` to the archive/restore GREEN review after all 44 candidate tests passed.
9. Approved Phase 3 after receiving browser-verification instructions. Requested review of AGENTS.md with only important verified commands, project structure, and durable conventions; no more than five added lines per phase and a final target of 60–80 lines maximum after ten phases; accurate Phase 3 logging here; review and staging of all Phase 3 changes; the exact commit message `Phase 3 Complete`; and a GitHub push with success confirmation. Explicitly prohibited starting Phase 4.

### Summary

- **Outcome:** Implemented Phase 3 only: case-insensitive name/email search with trimmed input, Active/Archived filtering, GET filter controls and reset/empty results, query-preserving pagination using Django's querystring tag, and staff-only CSRF-protected POST archive/restore actions with detail-page controls. Archived records remain viewable and editable with existing duplicate-email validation. All 81 tests passed, covering combined filters, pagination state, archived editing, record preservation, repeated submissions, ordinary/HTMX access control, HTTP methods, CSRF, and missing records. Ruff lint/format, Django system checks, migration consistency, and the CSS build passed; the local database needed no new migrations. User approved Phase 3 after receiving browser-verification steps. Added two durable conventions to AGENTS.md and marked Phase 3 approved in the plan. Finalization uses the requested commit message; the commit hash and verified push result are reported after Git verification.
- **Deviations:** No changes to Phase 3 scope. Paused for each required TDD checkpoint and manual-verification approval. Application preservation remains scheduled for Phase 6, when applications exist. No Phase 4 work was started.
- **Sideways:** An initial test-file read used the wrong path; located the existing recruiting/test_candidates.py. Sandbox restrictions blocked uv cache access; reran checks with approved escalation. Both selected TDD tests failed on their intended assertions before implementation. Pytest emitted an optional cache-write warning while all tests passed. Ruff caught line-length/import formatting issues; formatted three files and reran both checks successfully.

## 2026-10-31 — Phase 2 candidate entry and browsing

### Prompts

1. Supplied AGENTS.md project instructions and the Windows workspace context.
2. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 2 only.`
3. Supplied the implement skill: follow the PRD and plan, use the TDD skill with required approvals, run feedback loops, provide browser-verification steps and wait for confirmation, then update this log, commit, and push.
4. Answered `yes` to the two TDD selections: candidate email normalization/uniqueness and consistent admin email writes.
5. Answered `yes` to the first RED checkpoint: the form saved mixed-case email instead of lowercase; approved implementing normalization and duplicate feedback.
6. Answered `approved` to the first GREEN review after all 17 tests passed.
7. Answered `yes` to the admin RED checkpoint: its default form accepted a case/whitespace duplicate of an archived candidate; approved sharing CandidateForm with admin.
8. Answered `approved` to the admin GREEN review after all 18 tests passed.
9. Approved Phase 2 after receiving browser-verification instructions. Requested review of AGENTS.md with only important verified commands, project structure, and durable conventions; no more than five added lines per phase and a final target of 60–80 lines maximum after ten phases; accurate Phase 2 logging here; review and staging of all Phase 2 changes; the exact commit message `Phase 2 Complete`; and a GitHub push with success confirmation. Explicitly prohibited starting Phase 3.

### Summary

- **Outcome:** Implemented Phase 2 only: Candidate model and initial migration; shared staff/admin form validation; normalized model saves and unique email storage; all required and optional candidate fields and four source categories; staff-only create/detail/edit pages; escaped plain-text notes; a stable active-candidate list with 20 records per page; and shared navigation links. All 58 tests passed, covering validation, duplicate creation/editing including archived collisions, unchanged-email edits, admin writes, database duplicate rejection, field persistence, pagination, staff access for ordinary/HTMX requests, CSRF, HTTP methods, and missing records. Ruff lint/format checks, Django system checks, migration consistency, and the CSS build passed. Applied the migration locally, provided browser-verification steps, and received Phase 2 approval. Updated README and plan status and added three durable lines to AGENTS.md. Finalization uses the requested commit message; the commit hash and verified push result are reported after Git verification.
- **Deviations:** No changes to Phase 2 scope. Paused for all required TDD and manual-verification approvals. No Phase 3 search, filtering, or staff archive/restore actions were implemented.
- **Sideways:** Sandbox restrictions blocked uv cache access; reran required commands with approved escalation. Both TDD cycles failed on their intended assertions before implementation: mixed-case storage, then admin duplicate validation. Pytest initially warned that it could not write its cache; subsequent runs disabled that optional cache provider. Ruff formatted three files. No unresolved check failures remain.

## 2026-10-31 — Phase 1 staff authentication and project setup

### Prompts

1. Invoked `$implement @prd/applicant-tracking-system.md @plans/applicant-tracking-system.md implement Phase 1 only.`
2. Supplied the implement skill: read the approved documents, follow the TDD skill and approval checkpoints, run feedback loops, wait for manual-verification confirmation, then update this log, commit, and push.
3. Answered `approved` to selecting staff-only landing-page access for TDD, covering anonymous, non-staff, and staff users for ordinary and HTMX requests.
4. Answered `yes` to the failing test review: anonymous requests should redirect to sign-in, non-staff requests should receive 403, and staff requests should succeed.
5. Answered `yes` to the green-test review of the reusable staff-access decorator before the remaining Phase 1 work continued.
6. Approved Phase 1 after receiving browser-verification instructions. Requested that AGENTS.md gain no more than five lines of verified commands, project structure, and durable conventions, targeting 60–80 lines maximum after all ten phases; that this log accurately record Phase 1; and that all Phase 1 changes be reviewed, staged, committed with the exact message `Phase 1 Complete`, and pushed to GitHub. Explicitly prohibited starting Phase 2.

### Summary

- **Outcome:** Implemented Phase 1 only: a uv-managed Python/Django/SQLite project; Tailwind CSS and DaisyUI through django-tailwind-cli; locally served, pinned HTMX with its license; pytest/pytest-django and Ruff configuration; styled staff sign-in and a shared navigation/landing template; POST sign-out; a reusable staff-access decorator; and Django admin account administration. All 16 tests passed, as did Ruff lint/format checks, Django system and migration checks, and the CSS build. Applied built-in Django migrations locally and confirmed HTTP 200 responses for the login page, CSS, and HTMX assets. Provided browser-verification steps and received Phase 1 approval. Added five verified lines to AGENTS.md and updated README and the plan to reflect approval. Finalization uses the requested commit message; its commit hash and push result are reported to the user after Git verification.
- **Deviations:** No changes to the approved Phase 1 scope. Paused at each required TDD approval checkpoint and after browser-verification instructions. The user approved each checkpoint and requested the concise AGENTS.md update before committing. No Phase 2 functionality was implemented.
- **Sideways:** The system Python launcher was inaccessible, so uv used the installed Python 3.14 interpreter. Sandbox restrictions required approved access to uv's cache and dependency/asset downloads. The initial six-case access test correctly failed four assertions before the staff decorator made all six pass. The admin integration test initially omitted the required date-joined fields from its simulated edit submission; corrected that request, preserving the intended workflow. Removed unused generated imports and formatted the scaffold for Ruff. Tailwind status output initially failed under Windows console encoding; verified Python's `-X utf8` option and documented it. A sandbox-blocked CLI download succeeded with approved access, and the final stylesheet built successfully.

## 2026-10-31 — ATS requirements interview, prototypes, and PRD

### Prompts

1. Invoked `$grill-me` to design a new internal Applicant Tracking System. Required Python, Django, SQLite, uv, Tailwind CSS and DaisyUI through django-tailwind-cli, HTMX, Ruff, pytest, and pytest-django. Specified candidate and source management, Open/Closed openings, unique candidate-opening applications, eight application stages, HTMX stage updates, reusable skills, and decisions about candidate lifecycle and opening closure. Required stage-rule and pipeline-interface prototypes, one question at a time, simple conventional solutions, explicit prototype-topic notifications, incorporation of prototype decisions, and no implementation before concluding the interview and generating a PRD.
2. Supplied the `grill-me` skill instructions: settle design branches one question at a time, explain options and trade-offs, recommend an option, assume a beginner, and inspect the codebase when it can answer a question.
3. Supplied the `prototype` skill instructions, including logic/UI branches, throwaway standalone artifacts, in-memory state, visible state, and capturing decisions.
4. Supplied the `to-prd` skill instructions and required PRD template.
5. Answered `A`: all staff share access, with Django authentication and administrator-created accounts.
6. Answered `B`: candidate contact/source information plus optional internal notes, without résumé uploads.
7. Answered `A`: unique candidate emails, ignoring capitalization and surrounding whitespace.
8. Answered `a`: archive and restore candidates, preserving editable existing applications and blocking new applications while archived.
9. Answered `a`: openings contain title, description, Open/Closed status, and optional reusable skills.
10. Answered `a`: administrators maintain skills through Django admin; staff select existing skills.
11. Answered `a`: create applications for an existing active candidate and open opening, starting at Applied and blocking duplicate pairings.
12. Invoked `$prototype` at the application-stage-rules topic.
13. Supplied the `prototype` skill instructions again for that invocation.
14. Answered `a` after the stage-rules prototype: flexible changes between any stages, including terminal-state corrections; closed openings block new applications but permit existing stage changes; reopening preserves stages.
15. Answered `a`: applications store only candidate, opening, current stage, and automatic creation date, without application notes or stage history.
16. Invoked `$prototype` at the hiring-pipeline-interface topic.
17. Supplied the `prototype` skill instructions again for that invocation.
18. Answered `a` after the UI prototype: filterable table with inline stage dropdowns rather than a stage board or list/detail layout.
19. Answered `c`: allow staff to delete applications and openings, rather than omitting deletion from the staff interface.
20. Answered `c`: allow opening deletion only when it has no applications or all applications are Hired, Rejected, or Withdrawn.
21. Answered `a`: deleting an eligible opening also deletes its applications after confirmation, preserving candidate records.
22. Answered `a`: keep an application's candidate and opening fixed; correct mistaken pairings by deleting and recreating the application.
23. Answered `a`: simple searchable, paginated candidate/opening lists, status filters, and detail pages showing related applications and management actions.
24. Invoked `$to-prd` after the interview concluded.
25. Supplied the `to-prd` skill instructions again, directing synthesis into a local PRD without another interview.
26. Requested: "Write this session log to PROMPTS.md according to its instructions."

### Summary

- **Outcome:** Completed the requirements interview and both required prototypes. Kept `prototypes/application-stage-rules.html`, comparing three stage policies through free play and guided walkthroughs, and `prototypes/hiring-pipeline.html`, comparing a table, stage board, and list/detail interface. Recorded the chosen flexible rules and table interface in `prd/applicant-tracking-system.md`, along with the agreed technology, lifecycle, deletion, access, and browsing requirements. No production application was implemented.
- **Deviations:** Chose deletion of applications and openings instead of the recommended no-deletion policy. Chose terminal-stage eligibility for opening deletion instead of the recommended rule requiring applications to be deleted individually first. Chose minimal application data instead of recommended application notes. Other selected options followed the recommendations. No additional user follow-up questions or corrections were made beyond invoking the required prototypes and PRD skill.
- **Sideways:** While reviewing the stage-rules prototype, the agent found that adding a second candidate's application incorrectly depended on the first candidate's archived status. Removed that incorrect dependency and adjusted the archive walkthrough to demonstrate duplicate prevention and existing-application editing. The prototypes were saved and inspected as files, but were not browser-tested by the agent; the user selected both prototype directions. The UI prototype uses CDN assets with fallback styling and is separate from the eventual production asset pipeline.

This file is the record of AI use on this codebase. At the end of every
agent session, direct the agent to write the session log with this prompt:

> Append a session log to PROMPTS.md at the repo root, under today's date,
> newest entry at the top. Record every prompt I gave you this session, in
> order, including any corrections. End the entry with a short summary:
> the outcome, any places where I deviated from a recommended answer or
> asked follow-up questions, and anything that went sideways.

Two rules:

- Entries are added only by that prompt, never unprompted.
- New entries go at the top. Never rewrite or delete an old entry — the
  log is part of your work, and an honest log of a session that went
  sideways is worth more than a tidy one.

Each entry has this shape:

    ## YYYY-MM-DD — <one-line summary>

    ### Prompts
    1. ...

    ### Summary
    - **Outcome:** what was built and what was kept
    - **Deviations:** recommendations overridden, follow-up questions asked
    - **Sideways:** failures, wrong turns, and how they were caught
