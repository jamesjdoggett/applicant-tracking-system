import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize("htmx", [False, True], ids=["page", "htmx"])
@pytest.mark.parametrize(
    ("identity", "expected_status"),
    [("anonymous", 302), ("nonstaff", 403), ("staff", 200)],
)
def test_landing_page_requires_staff(
    client, django_user_model, identity, expected_status, htmx
):
    if identity != "anonymous":
        user = django_user_model.objects.create_user(
            username=identity, is_staff=identity == "staff"
        )
        client.force_login(user)

    url = reverse("recruiting:home")
    headers = {"HTTP_HX_REQUEST": "true"} if htmx else {}
    response = client.get(url, **headers)

    assert response.status_code == expected_status
    if identity == "anonymous":
        assert response.url == f"{reverse('login')}?next={url}"
    elif identity == "staff":
        assert b"Applicant Tracking System" in response.content
