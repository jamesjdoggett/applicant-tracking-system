# Project #1: Applicant Tracking System

Question 1 — Django Forms

My project uses `ApplicationStageForm` (`forms.Form`) to validate stage changes in the hiring pipeline. The form is submitted through HTMX to the `application_stage()` view, which validates and saves the new stage before updating the page. It also uses `OpeningForm` (`forms.ModelForm`) to create and edit job openings through the `opening_create()` and `opening_edit()` views, using the `opening_form.html` template. The main difference is that `forms.Form` requires manually defined fields and saving logic, while `forms.ModelForm` connects directly to a model and can save changes using `form.save()`.

Question 2 — Many-to-Many Relationship

The `Opening` and `Skill` models have a many-to-many relationship because each opening can require multiple skills, and each skill can belong to multiple openings. A single foreign key wouldn't support both sides of this relationship. Django automatically creates the `recruiting_opening_skills` association table using `ManyToManyField`, which connects openings and skills without duplicating records.

Question 3 — Prototype Decision

My application-state prototype compared three approaches: flexible stage changes, guided progression with corrections, and flexible changes that become restricted when an opening closes. I chose Policy A (flexible changes) because it allows staff to skip stages, move backward, and correct mistakes without unnecessary restrictions. This decision is documented in my PRD and implemented in the `application_stage()` view.

Question 4 — Code-Design Decision

I chose to keep the project in one Django app called `recruiting` rather than separating candidates, openings, skills, and applications into multiple apps. Since these features are closely related, keeping them together makes the project more simple to organize and navigate. This decision is reflected in `recruiting/models.py`, where all four models are defined, and in `config/settings.py`, where the app is registered.