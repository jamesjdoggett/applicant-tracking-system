import pytest
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
    assert b"View pipeline" in client.get(reverse("recruiting:home")).content


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
