from django.shortcuts import render

from .decorators import staff_required


@staff_required
def home(request):
    return render(request, "recruiting/home.html")
