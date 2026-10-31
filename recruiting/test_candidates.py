import pytest
from django.db import IntegrityError, transaction
from django.test import Client
from django.urls import reverse

from .forms import CandidateForm
from .models import Candidate

pytestmark = pytest.mark.django_db


def test_candidate_email_normalization_and_duplicate_feedback():
    data = {
        "name": "Alex Rivera",
        "email": "  Alex@Example.COM  ",
        "recruitment_source": "referrals",
    }
    create = CandidateForm(data)
    assert create.is_valid(), create.errors
    candidate = create.save()
    assert candidate.email == "alex@example.com"

    unchanged = CandidateForm(data, instance=candidate)
    assert unchanged.is_valid(), unchanged.errors
    unchanged.save()

    candidate.is_archived = True
    candidate.save()
    duplicate = CandidateForm({**data, "email": " ALEX@example.com "})
    assert not duplicate.is_valid()
    assert "email" in duplicate.errors

    other = Candidate.objects.create(
        name="Sam", email="sam@example.com", recruitment_source="job_boards"
    )
    edit = CandidateForm({**data, "email": " ALEX@example.com "}, instance=other)
    assert not edit.is_valid()
    assert "email" in edit.errors
    other.refresh_from_db()
    assert other.email == "sam@example.com"


def test_admin_normalizes_email_and_validates_duplicates(admin_client):
    data = {
        "name": "Admin candidate",
        "email": " Admin@Example.COM ",
        "recruitment_source": "company_website",
        "_save": "Save",
    }
    add_url = reverse("admin:recruiting_candidate_add")
    response = admin_client.post(add_url, data)
    assert response.status_code == 302
    candidate = Candidate.objects.get()
    assert candidate.email == "admin@example.com"

    change_url = reverse("admin:recruiting_candidate_change", args=[candidate.pk])
    response = admin_client.post(change_url, {**data, "email": candidate.email})
    assert response.status_code == 302

    candidate.is_archived = True
    candidate.save()
    response = admin_client.get(add_url)
    form_class = type(response.context["adminform"].form)
    duplicate = form_class({**data, "email": " ADMIN@example.com "})
    assert not duplicate.is_valid()
    assert "email" in duplicate.errors

    other = Candidate.objects.create(
        name="Other", email="other@example.com", recruitment_source="other"
    )
    change_url = reverse("admin:recruiting_candidate_change", args=[other.pk])
    response = admin_client.post(change_url, data)
    assert response.status_code == 200
    assert "email" in response.context["adminform"].form.errors
    other.refresh_from_db()
    assert other.email == "other@example.com"


@pytest.fixture
def staff(django_user_model):
    return django_user_model.objects.create_user(username="recruiter", is_staff=True)


@pytest.fixture
def candidate():
    return Candidate.objects.create(
        name="Alex Rivera", email="alex@example.com", recruitment_source="referrals"
    )


def test_staff_create_view_and_edit_candidate(client, staff):
    client.force_login(staff)
    create_url = reverse("recruiting:candidate_create")
    assert client.get(create_url).status_code == 200
    assert Candidate.objects.count() == 0
    data = {
        "name": "Alex Rivera",
        "email": " ALEX@Example.COM ",
        "recruitment_source": "job_boards",
        "phone": "+1 555 0100",
        "source_details": "University board",
        "notes": "<script>alert('test')</script>\nSecond line",
        "is_archived": "on",
    }
    response = client.post(create_url, data)
    candidate = Candidate.objects.get()
    detail_url = reverse("recruiting:candidate_detail", args=[candidate.pk])
    assert response.status_code == 302
    assert response.url == detail_url
    assert not candidate.is_archived
    assert candidate.email == "alex@example.com"
    for field in ("name", "recruitment_source", "phone", "source_details", "notes"):
        assert getattr(candidate, field) == data[field]

    response = client.get(detail_url)
    assert response.status_code == 200
    assert b"University board" in response.content
    assert b"Job boards" in response.content
    assert b"&lt;script&gt;" in response.content
    assert b"<script>alert" not in response.content
    assert b"Second line" in response.content

    edit_url = reverse("recruiting:candidate_edit", args=[candidate.pk])
    response = client.get(edit_url)
    assert response.context["form"].instance.pk == candidate.pk
    changes = {
        "name": "Alex Updated",
        "email": " Changed@Example.COM ",
        "recruitment_source": "other",
        "phone": "",
        "source_details": "Career fair",
        "notes": "Updated notes",
    }
    response = client.post(edit_url, changes)
    assert response.status_code == 302
    assert response.url == detail_url
    candidate.refresh_from_db()
    assert candidate.email == "changed@example.com"
    for field in ("name", "recruitment_source", "phone", "source_details", "notes"):
        assert getattr(candidate, field) == changes[field]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("email", ""),
        ("email", "invalid"),
        ("recruitment_source", ""),
        ("recruitment_source", "forged"),
    ],
)
def test_invalid_candidate_fields_are_not_saved(client, staff, field, value):
    client.force_login(staff)
    data = {"name": "Alex", "email": "alex@example.com", "recruitment_source": "other"}
    response = client.post(
        reverse("recruiting:candidate_create"), {**data, field: value}
    )
    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert b'role="alert"' in response.content
    assert not Candidate.objects.exists()


@pytest.mark.parametrize("source", Candidate.Source.values)
def test_approved_sources_and_optional_fields(source):
    form = CandidateForm(
        {"name": "Alex", "email": "alex@example.com", "recruitment_source": source}
    )
    assert form.is_valid(), form.errors
    candidate = form.save()
    assert candidate.recruitment_source == source
    assert (candidate.phone, candidate.source_details, candidate.notes) == ("", "", "")


def test_duplicate_posts_show_email_errors_without_changing_records(
    client, staff, candidate
):
    client.force_login(staff)
    candidate.is_archived = True
    candidate.save()
    data = {
        "name": "Duplicate",
        "email": " ALEX@Example.COM ",
        "recruitment_source": "other",
    }
    response = client.post(reverse("recruiting:candidate_create"), data)
    assert response.status_code == 200
    assert "email" in response.context["form"].errors
    other = Candidate.objects.create(
        name="Other", email="other@example.com", recruitment_source="other"
    )
    response = client.post(reverse("recruiting:candidate_edit", args=[other.pk]), data)
    assert response.status_code == 200
    assert "email" in response.context["form"].errors
    other.refresh_from_db()
    assert other.email == "other@example.com"
    assert Candidate.objects.count() == 2


def test_model_save_normalizes_email_and_database_rejects_duplicate(candidate):
    candidate.email = " Updated@Example.COM "
    candidate.save(update_fields=["email"])
    candidate.refresh_from_db()
    assert candidate.email == "updated@example.com"
    with transaction.atomic(), pytest.raises(IntegrityError):
        Candidate.objects.create(
            name="Duplicate", email=" UPDATED@example.com ", recruitment_source="other"
        )


def test_active_list_paginates_in_stable_name_order(client, staff):
    client.force_login(staff)
    url = reverse("recruiting:candidate_list")
    response = client.get(url)
    assert b"No active candidates yet" in response.content
    for index in range(21):
        Candidate.objects.create(
            name=f"Candidate {index:02}",
            email=f"{index}@example.com",
            recruitment_source="other",
        )
    Candidate.objects.create(
        name="Archived",
        email="archived@example.com",
        recruitment_source="other",
        is_archived=True,
    )
    first = client.get(url)
    page = first.context["page_obj"]
    assert page.paginator.count == 21
    assert [c.name for c in page] == [f"Candidate {i:02}" for i in range(20)]
    assert b"?page=2" in first.content
    second = client.get(url, {"page": 2})
    assert [c.name for c in second.context["page_obj"]] == ["Candidate 20"]
    assert b"?page=1" in second.content
    assert client.get(url, {"page": "invalid"}).context["page_obj"].number == 1


@pytest.mark.parametrize("htmx", [False, True])
@pytest.mark.parametrize("identity,status", [("anonymous", 302), ("nonstaff", 403)])
@pytest.mark.parametrize(
    "route,method",
    [
        ("candidate_list", "get"),
        ("candidate_detail", "get"),
        ("candidate_create", "get"),
        ("candidate_create", "post"),
        ("candidate_edit", "get"),
        ("candidate_edit", "post"),
    ],
)
def test_candidate_endpoints_require_staff(
    client, django_user_model, candidate, identity, status, route, method, htmx
):
    if identity == "nonstaff":
        client.force_login(django_user_model.objects.create_user(username="nonstaff"))
    args = [candidate.pk] if route in {"candidate_detail", "candidate_edit"} else []
    url = reverse(f"recruiting:{route}", args=args)
    response = getattr(client, method)(url, HTTP_HX_REQUEST="true" if htmx else "false")
    assert response.status_code == status
    assert Candidate.objects.count() == 1
    candidate.refresh_from_db()
    assert candidate.name == "Alex Rivera"


def test_candidate_mutations_require_csrf_and_read_pages_reject_posts(staff, candidate):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)
    data = {"name": "New", "email": "new@example.com", "recruitment_source": "other"}
    create_url = reverse("recruiting:candidate_create")
    edit_url = reverse("recruiting:candidate_edit", args=[candidate.pk])
    assert client.post(create_url, data).status_code == 403
    assert client.post(edit_url, data).status_code == 403
    client.get(create_url)
    data["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
    assert client.post(create_url, data).status_code == 302
    data["email"] = "edited@example.com"
    assert client.post(edit_url, data).status_code == 302
    for route, args in [("candidate_list", []), ("candidate_detail", [candidate.pk])]:
        assert (
            client.post(reverse(f"recruiting:{route}", args=args), data).status_code
            == 405
        )
    assert (
        client.put(edit_url, HTTP_X_CSRFTOKEN=data["csrfmiddlewaretoken"]).status_code
        == 405
    )


@pytest.mark.parametrize("route", ["candidate_detail", "candidate_edit"])
def test_missing_candidate_returns_404(client, staff, route):
    client.force_login(staff)
    assert client.get(reverse(f"recruiting:{route}", args=[999])).status_code == 404
