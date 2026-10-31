# PROMPTS.md — AI Usage Log

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
