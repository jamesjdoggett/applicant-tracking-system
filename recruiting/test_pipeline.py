import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

from .models import Application, Candidate, Opening

pytestmark = pytest.mark.django_db


def test_pipeline_search_opening_and_stage_filters_intersect(client, django_user_model):
    client.force_login(
        django_user_model.objects.create_user(username="staff", is_staff=True)
    )
    alex = Candidate.objects.create(
        name="Alex", email="alex@example.com", recruitment_source="other"
    )
    sam = Candidate.objects.create(
        name="Sam", email="sam@example.com", recruitment_source="other"
    )
    opening = Opening.objects.create(title="Developer", description="Tools")
    other = Opening.objects.create(title="Developer", description="Other team")
    expected = Application.objects.create(
        candidate=alex, opening=opening, stage="interview"
    )
    Application.objects.create(candidate=alex, opening=other, stage="interview")
    Application.objects.create(candidate=sam, opening=opening, stage="interview")
    Application.objects.create(candidate=sam, opening=other, stage="applied")

    response = client.get(
        reverse("recruiting:application_list"),
        {"q": "  ALEX@EXAMPLE  ", "opening": opening.pk, "stage": "interview"},
    )

    assert response.status_code == 200
    assert list(response.context["applications"]) == [expected]


@pytest.fixture
def pipeline(client, django_user_model):
    client.force_login(
        django_user_model.objects.create_user(username="staff", is_staff=True)
    )
    alex = Candidate.objects.create(
        name="Alex Rivera",
        email="alex@example.com",
        recruitment_source="other",
        is_archived=True,
    )
    sam = Candidate.objects.create(
        name="Sam", email="sam@example.com", recruitment_source="other"
    )
    closed = Opening.objects.create(
        title="Developer", description="Tools", status="closed"
    )
    opened = Opening.objects.create(title="Developer", description="Other team")
    first = Application.objects.create(candidate=alex, opening=closed, stage="hired")
    second = Application.objects.create(candidate=alex, opening=opened)
    third = Application.objects.create(candidate=sam, opening=opened, stage="hired")
    return first, second, third


def test_pipeline_filter_combinations_and_normalized_selections(client, pipeline):
    first, second, third = pipeline
    url = reverse("recruiting:application_list")
    cases = [
        ({}, [third, second, first]),
        ({"q": "  rIVera  "}, [second, first]),
        ({"q": "SAM@EXAMPLE"}, [third]),
        ({"opening": first.opening_id}, [first]),
        ({"opening": second.opening_id}, [third, second]),
        ({"stage": "hired"}, [third, first]),
        ({"opening": second.opening_id, "stage": "hired"}, [third]),
        ({"q": "alex", "stage": "hired"}, [first]),
        ({"q": "alex", "opening": second.opening_id}, [second]),
        ({"q": "sam", "opening": first.opening_id, "stage": "hired"}, []),
        ({"q": "  ", "opening": "invalid", "stage": "invalid"}, [third, second, first]),
        ({"opening": "9" * 100}, [third, second, first]),
    ]
    for params, expected in cases:
        response = client.get(url, params)
        assert response.status_code == 200
        assert list(response.context["applications"]) == expected
    response = client.get(
        url, {"q": "  Rivera  ", "opening": first.opening_id, "stage": "hired"}
    )
    assert b'value="Rivera"' in response.content
    assert f'value="{first.opening_id}" selected'.encode() in response.content
    assert b'value="hired" selected' in response.content


def test_pipeline_rows_include_archived_closed_records_and_detail_links(
    client, pipeline
):
    first, _, _ = pipeline
    response = client.get(reverse("recruiting:application_list"))
    for label in [
        "Candidate",
        "Email",
        "Opening",
        "Stage",
        "Created",
        "Alex Rivera",
        "alex@example.com",
        "Developer",
        "Hired",
    ]:
        assert label.encode() in response.content
    for route, pk in [
        ("candidate_detail", first.candidate_id),
        ("opening_detail", first.opening_id),
    ]:
        assert (
            f'href="{reverse(f"recruiting:{route}", args=[pk])}"'.encode()
            in response.content
        )
    created = timezone.localtime(first.created_at)
    assert date_format(created, "M j, Y").encode() in response.content
    assert f"#{first.opening_id}, Closed".encode() in response.content
    assert b"View applications" in client.get(reverse("recruiting:home")).content


def test_pipeline_empty_feedback_and_reset(client, django_user_model):
    client.force_login(
        django_user_model.objects.create_user(username="staff", is_staff=True)
    )
    url = reverse("recruiting:application_list")
    assert b"No applications yet" in client.get(url).content
    response = client.get(url, {"q": "missing"})
    assert b"No applications match these filters" in response.content
    assert f'href="{url}">Reset filters'.encode() in response.content


@pytest.mark.parametrize("htmx", [False, True])
@pytest.mark.parametrize("identity,status", [("anonymous", 302), ("nonstaff", 403)])
def test_pipeline_requires_staff(client, django_user_model, htmx, identity, status):
    if identity == "nonstaff":
        client.force_login(django_user_model.objects.create_user(username="nonstaff"))
    response = client.get(
        reverse("recruiting:application_list"),
        {"q": "Alex", "stage": "hired", "opening": 1},
        HTTP_HX_REQUEST="true" if htmx else "false",
    )
    assert response.status_code == status


def test_pipeline_is_read_only(client, pipeline):
    assert client.post(reverse("recruiting:application_list")).status_code == 405
    assert Application.objects.count() == 3


@pytest.mark.parametrize("initial_stage", Application.Stage.values)
@pytest.mark.parametrize("target_stage", Application.Stage.values)
@pytest.mark.parametrize("archived,closed", [(False, False), (True, True)])
def test_stage_changes_allow_every_transition(
    client, pipeline, initial_stage, target_stage, archived, closed
):
    application, _, _ = pipeline
    application.candidate.is_archived = archived
    application.candidate.save(update_fields=["is_archived"])
    application.opening.status = "closed" if closed else "open"
    application.opening.save(update_fields=["status"])
    application.stage = initial_stage
    application.save(update_fields=["stage"])

    response = client.post(
        reverse("recruiting:application_stage", args=[application.pk]),
        {"stage": target_stage},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    application.refresh_from_db()
    assert application.stage == target_stage


def test_stage_change_returns_current_filtered_fragment(client, pipeline):
    application, _, _ = pipeline
    url = reverse("recruiting:application_stage", args=[application.pk])
    response = client.post(
        f"{url}?q=++Alex++&opening={application.opening_id}&stage=hired",
        {"stage": "interview"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert b"Stage updated to Interview." in response.content
    assert b'id="pipeline-results"' in response.content
    assert b"No applications match these filters" in response.content
    assert list(response.context["applications"]) == []
    assert response.context["query"] == "Alex"
    assert response.context["opening_filter"] == str(application.opening_id)
    assert response.context["stage"] == "hired"
    assert b"<html" not in response.content
    application.refresh_from_db()
    assert application.stage == "interview"


@pytest.mark.parametrize("data", [{}, {"stage": ""}, {"stage": "invalid"}])
def test_invalid_stage_shows_error_and_preserves_application(client, pipeline, data):
    application, _, _ = pipeline
    original = (application.stage, application.candidate_id, application.opening_id)
    response = client.post(
        reverse("recruiting:application_stage", args=[application.pk]),
        data,
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert b"Stage was not changed. Select a valid stage." in response.content
    assert b'role="alert"' in response.content
    assert b"<html" not in response.content
    application.refresh_from_db()
    assert (
        application.stage,
        application.candidate_id,
        application.opening_id,
    ) == original
    assert f'value="{application.stage}" selected'.encode() in response.content


def test_stage_endpoint_ignores_pairing_and_date_overrides(client, pipeline):
    application, _, other = pipeline
    original = (
        application.candidate_id,
        application.opening_id,
        application.created_at,
    )
    response = client.post(
        reverse("recruiting:application_stage", args=[application.pk]),
        {
            "stage": "offer",
            "candidate": other.candidate_id,
            "opening": other.opening_id,
            "created_at": "2000-01-01",
        },
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    application.refresh_from_db()
    assert application.stage == "offer"
    assert (
        application.candidate_id,
        application.opening_id,
        application.created_at,
    ) == original
    other.refresh_from_db()
    assert other.stage == "hired"


@pytest.mark.parametrize("htmx", [False, True])
@pytest.mark.parametrize("identity,status", [("anonymous", 302), ("nonstaff", 403)])
def test_stage_endpoint_requires_staff(
    client, pipeline, django_user_model, htmx, identity, status
):
    application, _, _ = pipeline
    client.logout()
    if identity == "nonstaff":
        client.force_login(django_user_model.objects.create_user(username="nonstaff"))
    response = client.post(
        reverse("recruiting:application_stage", args=[application.pk]),
        {"stage": "interview"},
        HTTP_HX_REQUEST="true" if htmx else "false",
    )
    assert response.status_code == status
    application.refresh_from_db()
    assert application.stage == "hired"


@pytest.mark.parametrize("method", ["get", "head", "put", "patch", "delete"])
def test_stage_endpoint_requires_post(client, pipeline, method):
    application, _, _ = pipeline
    response = getattr(client, method)(
        reverse("recruiting:application_stage", args=[application.pk]),
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 405
    application.refresh_from_db()
    assert application.stage == "hired"


def test_stage_endpoint_requires_csrf(client, pipeline):
    application, _, _ = pipeline
    protected = Client(enforce_csrf_checks=True)
    protected.cookies = client.cookies.copy()
    url = reverse("recruiting:application_stage", args=[application.pk])
    assert (
        protected.post(url, {"stage": "interview"}, HTTP_HX_REQUEST="true").status_code
        == 403
    )
    application.refresh_from_db()
    assert application.stage == "hired"
    protected.get(reverse("recruiting:application_list"))
    token = protected.cookies["csrftoken"].value
    assert (
        protected.post(
            url, {"stage": "interview"}, HTTP_HX_REQUEST="true", HTTP_X_CSRFTOKEN=token
        ).status_code
        == 200
    )
    application.refresh_from_db()
    assert application.stage == "interview"


def test_stage_fragment_preserves_filters_and_inline_controls(client, pipeline):
    application, _, _ = pipeline
    url = reverse("recruiting:application_stage", args=[application.pk])
    response = client.post(
        f"{url}?q=Alex&opening={application.opening_id}&stage=hired",
        {"stage": "hired"},
        HTTP_HX_REQUEST="true",
    )
    assert list(response.context["applications"]) == [application]
    action = f"{url}?q=Alex&amp;opening={application.opening_id}&amp;stage=hired"
    assert f'hx-post="{action}"'.encode() in response.content
    for attribute in [
        'hx-trigger="change"',
        'hx-target="#pipeline-results"',
        'hx-swap="outerHTML"',
        'name="csrfmiddlewaretoken"',
    ]:
        assert attribute.encode() in response.content
    for value, label in Application.Stage.choices:
        assert f'value="{value}"'.encode() in response.content
        assert label.encode() in response.content


def test_stage_response_normalizes_invalid_filters_and_handles_missing_record(
    client, pipeline
):
    application, _, _ = pipeline
    url = reverse("recruiting:application_stage", args=[application.pk])
    response = client.post(
        f"{url}?q=++&opening=invalid&stage=invalid",
        {"stage": "interview"},
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert len(response.context["applications"]) == 3
    assert response.context["query"] == ""
    assert response.context["opening_filter"] == ""
    assert response.context["stage"] == ""
    assert (
        client.post(
            reverse("recruiting:application_stage", args=[999999]),
            {"stage": "interview"},
            HTTP_HX_REQUEST="true",
        ).status_code
        == 404
    )
