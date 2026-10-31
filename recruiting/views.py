from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .decorators import staff_required
from .forms import CandidateForm
from .models import Candidate


@staff_required
def home(request):
    return render(request, "recruiting/home.html")


@staff_required
@require_safe
def candidate_list(request):
    candidates = Candidate.objects.filter(is_archived=False)
    page = Paginator(candidates, 20).get_page(request.GET.get("page"))
    return render(request, "recruiting/candidate_list.html", {"page_obj": page})


@staff_required
@require_safe
def candidate_detail(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    return render(request, "recruiting/candidate_detail.html", {"candidate": candidate})


@staff_required
@require_http_methods(["GET", "POST"])
def candidate_create(request):
    form = CandidateForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        candidate = form.save()
        return redirect("recruiting:candidate_detail", pk=candidate.pk)
    return render(request, "recruiting/candidate_form.html", {"form": form})


@staff_required
@require_http_methods(["GET", "POST"])
def candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    form = CandidateForm(
        request.POST if request.method == "POST" else None, instance=candidate
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("recruiting:candidate_detail", pk=candidate.pk)
    return render(
        request,
        "recruiting/candidate_form.html",
        {"form": form, "candidate": candidate},
    )
