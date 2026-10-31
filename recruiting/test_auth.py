import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff(django_user_model):
    return django_user_model.objects.create_user(
        username="recruiter", password="Test-only-482!River", is_staff=True
    )


def test_staff_can_sign_in_and_sign_out(client, staff):
    login = client.get(reverse("login"))
    assert login.status_code == 200
    assert b"Sign in" in login.content

    response = client.post(
        reverse("login"),
        {"username": staff.username, "password": "Test-only-482!River"},
    )
    assert response.status_code == 302
    assert response.url == reverse("recruiting:home")
    home = client.get(response.url)
    assert home.status_code == 200
    assert b"Welcome, recruiter." in home.content
    assert b"Sign out" in home.content
    assert b"Manage staff accounts" not in home.content

    response = client.post(reverse("logout"))
    assert response.status_code == 302
    assert response.url == reverse("login")
    assert "_auth_user_id" not in client.session
    assert client.get(reverse("recruiting:home")).status_code == 302


@pytest.mark.parametrize("account", ["wrong_password", "nonstaff", "inactive"])
def test_rejected_sign_in_shows_error_without_creating_session(client, staff, account):
    if account == "nonstaff":
        staff.is_staff = False
        staff.save()
    elif account == "inactive":
        staff.is_active = False
        staff.save()
    password = "incorrect" if account == "wrong_password" else "Test-only-482!River"

    response = client.post(
        reverse("login"), {"username": staff.username, "password": password}
    )

    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert b'role="alert"' in response.content
    assert "_auth_user_id" not in client.session


@pytest.mark.parametrize("next_url", ["/?from=login", "https://example.com/"])
def test_sign_in_honors_only_local_next_url(client, staff, next_url):
    response = client.post(
        reverse("login"),
        {
            "username": staff.username,
            "password": "Test-only-482!River",
            "next": next_url,
        },
    )
    assert response.status_code == 302
    expected = next_url if next_url.startswith("/") else reverse("recruiting:home")
    assert response.url == expected


def test_sign_out_requires_post_and_csrf(staff):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)

    assert client.get(reverse("logout")).status_code == 405
    assert client.post(reverse("logout")).status_code == 403
    assert "_auth_user_id" in client.session

    client.get(reverse("recruiting:home"))
    response = client.post(
        reverse("logout"), {"csrfmiddlewaretoken": client.cookies["csrftoken"].value}
    )
    assert response.status_code == 302
    assert "_auth_user_id" not in client.session


def test_sign_in_requires_csrf(staff):
    client = Client(enforce_csrf_checks=True)
    data = {"username": staff.username, "password": "Test-only-482!River"}
    assert client.post(reverse("login"), data).status_code == 403

    client.get(reverse("login"))
    data["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
    assert client.post(reverse("login"), data).status_code == 302
    assert "_auth_user_id" in client.session


def test_administrator_can_create_and_enable_staff_account(
    admin_client, client, django_user_model
):
    response = admin_client.post(
        reverse("admin:auth_user_add"),
        {
            "username": "new-recruiter",
            "usable_password": "true",
            "password1": "Test-only-583!Forest",
            "password2": "Test-only-583!Forest",
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    user = django_user_model.objects.get(username="new-recruiter")
    assert user.check_password("Test-only-583!Forest")

    response = admin_client.post(
        reverse("admin:auth_user_change", args=[user.pk]),
        {
            "username": user.username,
            "is_active": "on",
            "is_staff": "on",
            "date_joined_0": user.date_joined.strftime("%Y-%m-%d"),
            "date_joined_1": user.date_joined.strftime("%H:%M:%S"),
            "_save": "Save",
        },
    )
    assert response.status_code == 302, response.context["adminform"].form.errors
    user.refresh_from_db()
    assert user.is_staff
    assert not user.is_superuser

    response = client.post(
        reverse("login"),
        {"username": user.username, "password": "Test-only-583!Forest"},
        follow=True,
    )
    assert response.status_code == 200
    assert b"Welcome, new-recruiter." in response.content


def test_staff_without_admin_permissions_cannot_manage_accounts(client, staff):
    client.force_login(staff)
    assert client.get(reverse("admin:auth_user_add")).status_code == 403
