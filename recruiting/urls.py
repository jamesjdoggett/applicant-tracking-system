from django.urls import path

from . import views

app_name = "recruiting"

urlpatterns = [path("", views.home, name="home")]
