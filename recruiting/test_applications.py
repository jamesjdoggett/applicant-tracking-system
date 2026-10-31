import pytest
from django.db import IntegrityError, transaction
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from .forms import ApplicationForm
from .models import Application, Candidate, Opening

pytestmark = pytest.mark.django_db


@pytest.fixture
def candidate():
    return Candidate.objects.create(
        name="Alex", email="alex@example.com", recruitment_source="other"
    )


@pytest.fixture
def opening():
    return Opening.objects.create(title="Developer", description="Build tools")


def test_duplicate_pairing_rejected_by_form_and_database_at_every_stage(
    candidate, opening
):
    application = Application.objects.create(candidate=candidate, opening=opening)
    for stage in Application.Stage.values:
        application.stage = stage
        application.save(update_fields=["stage"])
        form = ApplicationForm({"candidate": candidate.pk, "opening": opening.pk})
        assert not form.is_valid(), f"Duplicate accepted at {stage}"
        assert "already" in str(form.non_field_errors()).lower()
        with transaction.atomic(), pytest.raises(IntegrityError):
            Application.objects.create(candidate=candidate, opening=opening)
        assert Application.objects.count() == 1


def test_creation_rechecks_eligibility_after_form_load_and_allows_reopening(
    client, django_user_model, candidate, opening
):
    client.force_login(
        django_user_model.objects.create_user(username="staff", is_staff=True)
    )
    url = reverse("recruiting:application_create")
    data = {"candidate": candidate.pk, "opening": opening.pk}
    assert client.get(url, data).status_code == 200
    candidate.is_archived = True
    candidate.save(update_fields=["is_archived"])
    response = client.post(url, data)
    assert response.status_code == 200
    assert "candidate" in response.context["form"].errors
    assert not Application.objects.exists()

    candidate.is_archived = False
    candidate.save(update_fields=["is_archived"])
    assert client.get(url, data).status_code == 200
    opening.status = Opening.Status.CLOSED
    opening.save(update_fields=["status"])
    response = client.post(url, data)
    assert response.status_code == 200
    assert "opening" in response.context["form"].errors
    assert not Application.objects.exists()

    opening.status = Opening.Status.OPEN
    opening.save(update_fields=["status"])
    assert client.post(url, data).status_code == 302
    application = Application.objects.get()
    assert application.candidate == candidate
    assert application.opening == opening
    assert application.stage == Application.Stage.APPLIED


@pytest.fixture
def staff(django_user_model):
    return django_user_model.objects.create_user(username="recruiter", is_staff=True)


def test_confirmed_deletion_removes_only_selected_application(
    client, staff, candidate, opening
):
    client.force_login(staff)
    application = Application.objects.create(candidate=candidate, opening=opening)
    other_opening = Opening.objects.create(title="Designer", description="Design tools")
    other_application = Application.objects.create(
        candidate=candidate, opening=other_opening, stage=Application.Stage.INTERVIEW
    )
    response = client.post(
        reverse("recruiting:application_delete", args=[application.pk])
    )
    assert response.status_code == 302
    assert not Application.objects.filter(pk=application.pk).exists()
    assert Application.objects.get(pk=other_application.pk).stage == "interview"
    assert Candidate.objects.filter(pk=candidate.pk).exists()
    assert Opening.objects.filter(pk=opening.pk).exists()
    assert Opening.objects.filter(pk=other_opening.pk).exists()


def test_deletion_confirmation_cancel_and_management_links(
    client, staff, candidate, opening
):
    client.force_login(staff)
    application = Application.objects.create(candidate=candidate, opening=opening)
    url = reverse("recruiting:application_delete", args=[application.pk])
    pipeline_url = reverse("recruiting:application_list")
    for page in [
        pipeline_url,
        reverse("recruiting:candidate_detail", args=[candidate.pk]),
        reverse("recruiting:opening_detail", args=[opening.pk]),
    ]:
        assert f'href="{url}"'.encode() in client.get(page).content
    response = client.get(url)
    assert response.status_code == 200
    for label in [candidate.name, candidate.email, opening.title, f"#{opening.pk}"]:
        assert label.encode() in response.content
    assert f'action="{url}"'.encode() in response.content
    assert b'name="csrfmiddlewaretoken"' in response.content
    assert f'href="{pipeline_url}">Cancel</a>'.encode() in response.content
    assert client.get(pipeline_url).status_code == 200
    assert Application.objects.get(pk=application.pk).stage == "applied"


@pytest.mark.parametrize("stage", Application.Stage.values)
@pytest.mark.parametrize(
    "archived,status",
    [(False, "open"), (True, "open"), (False, "closed"), (True, "closed")],
)
def test_deletion_at_every_stage_and_replacement_eligibility(
    client, staff, candidate, opening, stage, archived, status
):
    client.force_login(staff)
    candidate.is_archived = archived
    candidate.save(update_fields=["is_archived"])
    opening.status = status
    opening.save(update_fields=["status"])
    application = Application.objects.create(
        candidate=candidate, opening=opening, stage=stage
    )
    original_pk = application.pk
    original_created_at = application.created_at
    url = reverse("recruiting:application_delete", args=[original_pk])
    assert client.get(url).status_code == 200
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("recruiting:application_list")
    assert not Application.objects.exists()
    candidate.refresh_from_db()
    opening.refresh_from_db()
    assert candidate.is_archived == archived
    assert opening.status == status
    response = client.post(
        reverse("recruiting:application_create"),
        {"candidate": candidate.pk, "opening": opening.pk, "stage": stage},
    )
    if archived or status == "closed":
        assert response.status_code == 200
        assert response.context["form"].errors
        assert not Application.objects.exists()
    else:
        assert response.status_code == 302
        replacement = Application.objects.get()
        assert replacement.pk != original_pk
        assert replacement.stage == Application.Stage.APPLIED
        assert replacement.created_at >= original_created_at
        assert (replacement.candidate_id, replacement.opening_id) == (
            candidate.pk,
            opening.pk,
        )


@pytest.mark.parametrize("identity,expected", [("anonymous", 302), ("nonstaff", 403)])
@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize("htmx", [False, True])
def test_deletion_requires_staff(
    client, django_user_model, candidate, opening, identity, expected, method, htmx
):
    application = Application.objects.create(candidate=candidate, opening=opening)
    if identity == "nonstaff":
        client.force_login(django_user_model.objects.create_user(username="nonstaff"))
    response = getattr(client, method)(
        reverse("recruiting:application_delete", args=[application.pk]),
        HTTP_HX_REQUEST="true" if htmx else "false",
    )
    assert response.status_code == expected
    assert Application.objects.filter(pk=application.pk).exists()


def test_deletion_csrf_methods_and_missing_records(staff, candidate, opening):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)
    application = Application.objects.create(candidate=candidate, opening=opening)
    url = reverse("recruiting:application_delete", args=[application.pk])
    assert client.post(url).status_code == 403
    assert client.get(url).status_code == 200
    token = client.cookies["csrftoken"].value
    for method in ["put", "patch", "delete", "options"]:
        assert getattr(client, method)(url, HTTP_X_CSRFTOKEN=token).status_code == 405
    assert client.head(url).status_code == 405
    assert Application.objects.filter(pk=application.pk).exists()
    assert client.post(url, {"csrfmiddlewaretoken": token}).status_code == 302
    assert not Application.objects.filter(pk=application.pk).exists()
    assert client.get(url).status_code == 404
    assert client.post(url, {"csrfmiddlewaretoken": token}).status_code == 404


@pytest.mark.parametrize("context", ["candidate", "opening"])
def test_creation_from_both_contexts_ignores_stage_and_date_overrides(
    client, staff, candidate, opening, context
):
    client.force_login(staff)
    record = candidate if context == "candidate" else opening
    url = reverse("recruiting:application_create") + f"?{context}={record.pk}"
    response = client.get(url)
    assert response.context["form"].initial[context] == record
    assert set(response.context["form"].fields) == {"candidate", "opening"}
    assert not Application.objects.exists()
    before = timezone.now()
    response = client.post(
        url,
        {
            "candidate": candidate.pk,
            "opening": opening.pk,
            "stage": "hired",
            "created_at": "2000-01-01",
            "id": 999,
        },
    )
    assert response.status_code == 302
    assert response.url == reverse(f"recruiting:{context}_detail", args=[record.pk])
    application = Application.objects.get()
    assert application.stage == "applied"
    assert before <= application.created_at <= timezone.now()
    assert application.pk != 999
    detail = client.get(response.url)
    assert list(detail.context["applications"]) == [application]
    assert b"Applied" in detail.content


def test_candidate_and_opening_can_have_multiple_applications(
    client, staff, candidate, opening
):
    client.force_login(staff)
    other_candidate = Candidate.objects.create(
        name="Sam", email="sam@example.com", recruitment_source="other"
    )
    other_opening = Opening.objects.create(
        title=opening.title, description="Other team"
    )
    url = reverse("recruiting:application_create")
    for person, role in [
        (candidate, opening),
        (candidate, other_opening),
        (other_candidate, opening),
    ]:
        assert (
            client.post(url, {"candidate": person.pk, "opening": role.pk}).status_code
            == 302
        )
    assert candidate.applications.count() == 2
    assert opening.applications.count() == 2
    response = client.get(reverse("recruiting:candidate_detail", args=[candidate.pk]))
    assert len(response.context["applications"]) == 2
    for role in [opening, other_opening]:
        assert (
            reverse("recruiting:opening_detail", args=[role.pk]).encode()
            in response.content
        )
    response = client.get(reverse("recruiting:opening_detail", args=[opening.pk]))
    assert len(response.context["applications"]) == 2
    for person in [candidate, other_candidate]:
        assert person.email.encode() in response.content


@pytest.mark.parametrize("stage", Application.Stage.values)
def test_duplicate_posts_report_error_and_preserve_existing_application(
    client, staff, candidate, opening, stage
):
    client.force_login(staff)
    application = Application.objects.create(
        candidate=candidate, opening=opening, stage=stage
    )
    response = client.post(
        reverse("recruiting:application_create"),
        {
            "candidate": candidate.pk,
            "opening": opening.pk,
        },
    )
    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert b"already exists" in response.content
    assert Application.objects.count() == 1
    application.refresh_from_db()
    assert application.stage == stage


@pytest.mark.parametrize(
    "field,value",
    [
        ("candidate", ""),
        ("opening", ""),
        ("candidate", 999),
        ("opening", 999),
        ("candidate", "forged"),
        ("opening", "forged"),
    ],
)
def test_invalid_application_fields_are_not_saved(
    client, staff, candidate, opening, field, value
):
    client.force_login(staff)
    data = {"candidate": candidate.pk, "opening": opening.pk, field: value}
    response = client.post(reverse("recruiting:application_create"), data)
    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert not Application.objects.exists()


def test_creation_choices_exclude_archived_candidates_and_closed_openings(
    candidate, opening
):
    archived = Candidate.objects.create(
        name="Archived",
        email="archived@example.com",
        recruitment_source="other",
        is_archived=True,
    )
    closed = Opening.objects.create(
        title="Closed", description="Old role", status="closed"
    )
    form = ApplicationForm()
    assert list(form.fields["candidate"].queryset) == [candidate]
    assert list(form.fields["opening"].queryset) == [opening]
    forged = ApplicationForm({"candidate": archived.pk, "opening": closed.pk})
    assert not forged.is_valid()
    assert set(forged.errors) == {"candidate", "opening"}


@pytest.mark.parametrize("stage", Application.Stage.values)
def test_lifecycle_changes_preserve_applications_on_both_details(
    client, staff, candidate, opening, stage
):
    client.force_login(staff)
    application = Application.objects.create(
        candidate=candidate, opening=opening, stage=stage
    )
    created_at = application.created_at
    candidate_url = reverse("recruiting:candidate_detail", args=[candidate.pk])
    opening_url = reverse("recruiting:opening_detail", args=[opening.pk])
    create_url = reverse("recruiting:application_create")
    assert (
        f"{create_url}?candidate={candidate.pk}".encode()
        in client.get(candidate_url).content
    )
    assert (
        f"{create_url}?opening={opening.pk}".encode() in client.get(opening_url).content
    )
    assert (
        client.post(
            reverse("recruiting:candidate_archive", args=[candidate.pk])
        ).status_code
        == 302
    )
    edit = reverse("recruiting:opening_edit", args=[opening.pk])
    for status in ["closed", "open"]:
        assert (
            client.post(
                edit,
                {
                    "title": opening.title,
                    "description": opening.description,
                    "status": status,
                },
            ).status_code
            == 302
        )
        for url in [candidate_url, opening_url]:
            response = client.get(url)
            assert list(response.context["applications"]) == [application]
            assert application.get_stage_display().encode() in response.content
        assert (
            f"{create_url}?candidate={candidate.pk}".encode()
            not in client.get(candidate_url).content
        )
        if status == "closed":
            assert (
                f"{create_url}?opening={opening.pk}".encode()
                not in client.get(opening_url).content
            )
        application.refresh_from_db()
        assert (application.stage, application.created_at) == (stage, created_at)
        assert (application.candidate_id, application.opening_id) == (
            candidate.pk,
            opening.pk,
        )
    assert (
        client.post(
            reverse("recruiting:candidate_restore", args=[candidate.pk])
        ).status_code
        == 302
    )
    assert (
        f"{create_url}?candidate={candidate.pk}".encode()
        in client.get(candidate_url).content
    )


@pytest.mark.parametrize("identity,status", [("anonymous", 302), ("nonstaff", 403)])
@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize("htmx", [False, True])
def test_application_creation_requires_staff(
    client, django_user_model, candidate, opening, identity, status, method, htmx
):
    if identity == "nonstaff":
        client.force_login(django_user_model.objects.create_user(username="nonstaff"))
    response = getattr(client, method)(
        reverse("recruiting:application_create"),
        {
            "candidate": candidate.pk,
            "opening": opening.pk,
        },
        HTTP_HX_REQUEST="true" if htmx else "false",
    )
    assert response.status_code == status
    assert not Application.objects.exists()


def test_creation_csrf_methods_and_no_pairing_edit_route(staff, candidate, opening):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)
    url = reverse("recruiting:application_create")
    data = {"candidate": candidate.pk, "opening": opening.pk}
    assert client.post(url, data).status_code == 403
    client.get(url)
    token = client.cookies["csrftoken"].value
    assert client.put(url, HTTP_X_CSRFTOKEN=token).status_code == 405
    assert client.post(url, {**data, "csrfmiddlewaretoken": token}).status_code == 302
    application = Application.objects.get()
    assert client.get(f"/applications/{application.pk}/edit/").status_code == 404
    assert (
        client.post(
            f"/applications/{application.pk}/edit/",
            {
                **data,
                "candidate": 999,
                "csrfmiddlewaretoken": token,
            },
        ).status_code
        == 404
    )
    application.refresh_from_db()
    assert (application.candidate_id, application.opening_id) == (
        candidate.pk,
        opening.pk,
    )


@pytest.mark.parametrize("field", ["candidate", "opening"])
@pytest.mark.parametrize("value", ["999", "invalid"])
def test_invalid_creation_context_returns_404(client, staff, field, value):
    client.force_login(staff)
    assert (
        client.get(reverse("recruiting:application_create"), {field: value}).status_code
        == 404
    )
