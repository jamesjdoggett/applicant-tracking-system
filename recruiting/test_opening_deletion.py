import pytest
from django.test import Client
from django.urls import reverse

from .models import Application, Candidate, Opening, Skill

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("status", Opening.Status.values)
@pytest.mark.parametrize("stage", [None, *Application.Stage.values])
def test_opening_deletion_eligibility(client, django_user_model, status, stage):
    staff = django_user_model.objects.create_user(username="staff", is_staff=True)
    client.force_login(staff)
    opening = Opening.objects.create(
        title="Developer", description="Build tools.", status=status
    )
    if stage is not None:
        candidate = Candidate.objects.create(
            name="Alex", email="alex@example.com", recruitment_source="other"
        )
        Application.objects.create(candidate=candidate, opening=opening, stage=stage)

    response = client.post(reverse("recruiting:opening_delete", args=[opening.pk]))

    eligible = stage in {None, "hired", "rejected", "withdrawn"}
    assert response.status_code == (302 if eligible else 200)
    assert Opening.objects.filter(pk=opening.pk).exists() is not eligible
    if eligible:
        assert response.url == reverse("recruiting:opening_list")
    else:
        assert Application.objects.filter(opening=opening, stage=stage).exists()
        assert b"cannot be deleted" in response.content


def test_opening_deletion_rechecks_stage_after_confirmation(client, django_user_model):
    staff = django_user_model.objects.create_user(username="staff", is_staff=True)
    client.force_login(staff)
    candidate = Candidate.objects.create(
        name="Alex", email="alex@example.com", recruitment_source="other"
    )
    opening = Opening.objects.create(title="Developer", description="Build tools.")
    application = Application.objects.create(
        candidate=candidate, opening=opening, stage=Application.Stage.HIRED
    )
    url = reverse("recruiting:opening_delete", args=[opening.pk])
    confirmation = client.get(url)
    assert confirmation.status_code == 200
    assert b"Delete opening and applications" in confirmation.content

    stage_response = client.post(
        reverse("recruiting:application_stage", args=[application.pk]),
        {"stage": Application.Stage.INTERVIEW},
        HTTP_HX_REQUEST="true",
    )
    assert stage_response.status_code == 200
    response = client.post(url)

    assert response.status_code == 200
    assert b"cannot be deleted" in response.content
    assert b"Delete opening and applications" not in response.content
    assert Opening.objects.filter(pk=opening.pk).exists()
    application.refresh_from_db()
    assert application.stage == Application.Stage.INTERVIEW


@pytest.fixture
def deletion_records(client, django_user_model):
    staff = django_user_model.objects.create_user(username="staff", is_staff=True)
    client.force_login(staff)
    opening = Opening.objects.create(title="Developer", description="Build tools.")
    applications = []
    for index, stage in enumerate(["hired", "rejected", "withdrawn"]):
        candidate = Candidate.objects.create(
            name=f"Candidate {index}",
            email=f"candidate{index}@example.com",
            recruitment_source="other",
            is_archived=True,
        )
        applications.append(
            Application.objects.create(
                candidate=candidate, opening=opening, stage=stage
            )
        )
    return staff, opening, applications


def test_confirmation_cancel_and_cascade_preserve_other_records(
    client, deletion_records
):
    _, opening, applications = deletion_records
    skill = Skill.objects.create(name="Python")
    opening.skills.add(skill)
    other = Opening.objects.create(title=opening.title, description="Another role")
    other.skills.add(skill)
    unrelated = Application.objects.create(
        opening=other, candidate=applications[0].candidate
    )
    url = reverse("recruiting:opening_delete", args=[opening.pk])
    detail_url = reverse("recruiting:opening_detail", args=[opening.pk])
    assert url.encode() in client.get(detail_url).content
    response = client.get(url)
    assert response.status_code == 200
    assert f"{opening.title} (#{opening.pk})".encode() in response.content
    assert b"csrfmiddlewaretoken" in response.content
    assert f'href="{detail_url}"'.encode() in response.content
    for application in applications:
        assert f"#{application.pk}".encode() in response.content
        assert application.candidate.name.encode() in response.content
        assert application.candidate.email.encode() in response.content
        assert application.get_stage_display().encode() in response.content
    assert client.get(detail_url).status_code == 200  # Follow Cancel.
    assert opening.applications.count() == 3
    assert client.post(url).status_code == 302
    assert not Opening.objects.filter(pk=opening.pk).exists()
    assert not Application.objects.filter(pk__in=[a.pk for a in applications]).exists()
    assert Candidate.objects.count() == 3
    assert Skill.objects.filter(pk=skill.pk).exists()
    assert list(other.skills.all()) == [skill]
    assert Application.objects.filter(pk=unrelated.pk).exists()


@pytest.mark.parametrize(
    "stage", ["applied", "screening", "interview", "final_review", "offer"]
)
def test_mixed_terminal_and_nonterminal_stages_block_deletion(
    client, deletion_records, stage
):
    _, opening, applications = deletion_records
    application = applications[0]
    application.stage = stage
    application.save(update_fields=["stage"])
    url = reverse("recruiting:opening_delete", args=[opening.pk])
    for method in [client.get, client.post]:
        response = method(url)
        assert response.status_code == 200
        assert b"cannot be deleted" in response.content
        assert b"Delete opening and applications" not in response.content
        assert opening.applications.count() == 3
        assert Opening.objects.filter(pk=opening.pk).exists()


@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize("identity,status", [("anonymous", 302), ("nonstaff", 403)])
@pytest.mark.parametrize("htmx", [False, True])
def test_opening_deletion_requires_staff(
    client, django_user_model, deletion_records, method, identity, status, htmx
):
    _, opening, _ = deletion_records
    client.logout()
    if identity == "nonstaff":
        client.force_login(django_user_model.objects.create_user(username="nonstaff"))
    response = getattr(client, method)(
        reverse("recruiting:opening_delete", args=[opening.pk]),
        HTTP_HX_REQUEST="true" if htmx else "false",
    )
    assert response.status_code == status
    assert Opening.objects.filter(pk=opening.pk).exists()
    assert opening.applications.count() == 3


def test_opening_deletion_csrf_methods_and_missing_record(deletion_records):
    staff, opening, _ = deletion_records
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)
    url = reverse("recruiting:opening_delete", args=[opening.pk])
    assert client.post(url).status_code == 403
    assert opening.applications.count() == 3
    assert client.get(url).status_code == 200
    token = client.cookies["csrftoken"].value
    for method in [client.put, client.patch, client.delete, client.head]:
        assert method(url, HTTP_X_CSRFTOKEN=token).status_code == 405
    assert Opening.objects.filter(pk=opening.pk).exists()
    assert client.post(url, {"csrfmiddlewaretoken": token}).status_code == 302
    assert client.get(url).status_code == 404
    assert client.post(url, {"csrfmiddlewaretoken": token}).status_code == 404
