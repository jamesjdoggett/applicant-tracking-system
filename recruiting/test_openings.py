import pytest
from django.db import IntegrityError, transaction
from django.test import Client
from django.urls import reverse

from .models import Opening, Skill

pytestmark = pytest.mark.django_db


def test_staff_create_and_edit_opening_skill_selection(client, django_user_model):
    staff = django_user_model.objects.create_user(username="recruiter", is_staff=True)
    client.force_login(staff)
    python = Skill.objects.create(name="Python")
    django = Skill.objects.create(name="Django")
    sqlite = Skill.objects.create(name="SQLite")
    data = {
        "title": "Developer",
        "description": "Build internal tools.",
        "status": "open",
        "skills": [python.pk, django.pk],
    }
    response = client.post(reverse("recruiting:opening_create"), data)
    assert response.status_code == 302
    opening = Opening.objects.get()
    assert set(opening.skills.all()) == {python, django}

    edit_url = reverse("recruiting:opening_edit", args=[opening.pk])
    response = client.post(
        edit_url, {**data, "status": "closed", "skills": [sqlite.pk]}
    )
    assert response.status_code == 302
    opening.refresh_from_db()
    assert opening.status == "closed"
    assert set(opening.skills.all()) == {sqlite}

    response = client.post(edit_url, {**data, "skills": []})
    assert response.status_code == 302
    assert not opening.skills.exists()


@pytest.fixture
def staff(django_user_model):
    return django_user_model.objects.create_user(username="staff", is_staff=True)


@pytest.fixture
def opening():
    return Opening.objects.create(title="Developer", description="Build tools.")


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", ""),
        ("description", ""),
        ("status", ""),
        ("status", "forged"),
        ("skills", [999]),
    ],
)
def test_invalid_opening_fields_do_not_change_records(
    client, staff, opening, field, value
):
    client.force_login(staff)
    data = {"title": "Changed", "description": "New description", "status": "closed"}
    for route, args in [("opening_create", []), ("opening_edit", [opening.pk])]:
        response = client.post(
            reverse(f"recruiting:{route}", args=args), {**data, field: value}
        )
        assert response.status_code == 200
        assert field in response.context["form"].errors
        assert b'role="alert"' in response.content
    opening.refresh_from_db()
    assert opening.title == "Developer"
    assert opening.status == "open"
    assert Opening.objects.count() == 1


def test_duplicate_titles_optional_skills_and_escaped_details(client, staff, opening):
    client.force_login(staff)
    response = client.post(
        reverse("recruiting:opening_create"),
        {
            "title": opening.title,
            "description": "<script>test</script>\nNext line",
            "status": "closed",
        },
    )
    assert response.status_code == 302
    created = Opening.objects.exclude(pk=opening.pk).get()
    assert not created.skills.exists()
    response = client.get(response.url)
    assert b"&lt;script&gt;test&lt;/script&gt;" in response.content
    assert b"<script>test" not in response.content
    assert b"Next line" in response.content
    assert b"Closed" in response.content
    assert b"No skills selected" in response.content


def test_admin_manages_unique_shared_skills(admin_client):
    add = reverse("admin:recruiting_skill_add")
    assert (
        admin_client.post(add, {"name": "Python", "_save": "Save"}).status_code == 302
    )
    skill = Skill.objects.get()
    response = admin_client.post(add, {"name": "Python", "_save": "Save"})
    assert response.status_code == 200
    assert "name" in response.context["adminform"].form.errors
    with transaction.atomic(), pytest.raises(IntegrityError):
        Skill.objects.create(name="Python")
    change = reverse("admin:recruiting_skill_change", args=[skill.pk])
    assert (
        admin_client.post(change, {"name": "Django", "_save": "Save"}).status_code
        == 302
    )
    skill.refresh_from_db()
    assert skill.name == "Django"
    delete = reverse("admin:recruiting_skill_delete", args=[skill.pk])
    assert admin_client.post(delete, {"post": "yes"}).status_code == 302
    assert not Skill.objects.exists()


def test_opening_forms_and_details_show_existing_skills(client, staff, opening):
    client.force_login(staff)
    skill = Skill.objects.create(name="Python")
    opening.skills.add(skill)
    create = client.get(reverse("recruiting:opening_create"))
    assert b'<select name="skills"' in create.content
    assert b"multiple" in create.content
    assert b"Python" in create.content
    edit = client.get(reverse("recruiting:opening_edit", args=[opening.pk]))
    assert list(edit.context["form"].initial["skills"]) == [skill]
    detail = client.get(reverse("recruiting:opening_detail", args=[opening.pk]))
    assert b"Python" in detail.content
    assert b"Build tools." in detail.content
    assert b"Open" in detail.content


def test_opening_list_paginates_both_statuses_in_stable_order(client, staff):
    client.force_login(staff)
    url = reverse("recruiting:opening_list")
    assert b"No openings yet" in client.get(url).content
    for index in range(21):
        Opening.objects.create(
            title=f"Role {index:02}",
            description="Description",
            status="closed" if index % 2 else "open",
        )
    first = client.get(url)
    assert first.context["page_obj"].paginator.count == 21
    assert [o.title for o in first.context["page_obj"]] == [
        f"Role {i:02}" for i in range(20)
    ]
    assert b"?page=2" in first.content
    second = client.get(url, {"page": 2})
    assert [o.title for o in second.context["page_obj"]] == ["Role 20"]
    assert b"?page=1" in second.content
    assert client.get(url, {"page": "invalid"}).context["page_obj"].number == 1


@pytest.mark.parametrize("htmx", [False, True])
@pytest.mark.parametrize("identity,status", [("anonymous", 302), ("nonstaff", 403)])
@pytest.mark.parametrize(
    "route,method",
    [
        ("opening_list", "get"),
        ("opening_detail", "get"),
        ("opening_create", "get"),
        ("opening_create", "post"),
        ("opening_edit", "get"),
        ("opening_edit", "post"),
    ],
)
def test_opening_endpoints_require_staff(
    client, django_user_model, opening, htmx, identity, status, route, method
):
    if identity == "nonstaff":
        client.force_login(django_user_model.objects.create_user(username="nonstaff"))
    args = [] if route in {"opening_list", "opening_create"} else [opening.pk]
    response = getattr(client, method)(
        reverse(f"recruiting:{route}", args=args),
        HTTP_HX_REQUEST="true" if htmx else "false",
    )
    assert response.status_code == status
    assert Opening.objects.count() == 1
    opening.refresh_from_db()
    assert opening.title == "Developer"


def test_opening_csrf_and_allowed_methods(staff, opening):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)
    create = reverse("recruiting:opening_create")
    edit = reverse("recruiting:opening_edit", args=[opening.pk])
    data = {"title": "New", "description": "Description", "status": "open"}
    for url in [create, edit]:
        assert client.post(url, data).status_code == 403
    client.get(create)
    token = client.cookies["csrftoken"].value
    data["csrfmiddlewaretoken"] = token
    for url in [create, edit]:
        assert client.post(url, data).status_code == 302
        assert client.put(url, HTTP_X_CSRFTOKEN=token).status_code == 405
    for route, args in [("opening_list", []), ("opening_detail", [opening.pk])]:
        assert (
            client.post(reverse(f"recruiting:{route}", args=args), data).status_code
            == 405
        )


@pytest.mark.parametrize("route", ["opening_detail", "opening_edit"])
def test_missing_opening_returns_404(client, staff, route):
    client.force_login(staff)
    assert client.get(reverse(f"recruiting:{route}", args=[999])).status_code == 404
