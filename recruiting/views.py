from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from .decorators import staff_required
from .forms import CandidateForm, OpeningForm
from .models import Candidate, Opening


@staff_required
@require_safe
def opening_list(request):
    page = Paginator(Opening.objects.all(), 20).get_page(request.GET.get("page"))
    return render(request, "recruiting/opening_list.html", {"page_obj": page})


@staff_required
@require_http_methods(["GET", "POST"])
def opening_create(request):
    form = OpeningForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        opening = form.save()
        return redirect("recruiting:opening_detail", pk=opening.pk)
    return render(request, "recruiting/opening_form.html", {"form": form})


@staff_required
@require_http_methods(["GET", "POST"])
def opening_edit(request, pk):
    opening = get_object_or_404(Opening, pk=pk)
    form = OpeningForm(
        request.POST if request.method == "POST" else None, instance=opening
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("recruiting:opening_detail", pk=opening.pk)
    return render(
        request, "recruiting/opening_form.html", {"form": form, "opening": opening}
    )


@staff_required
@require_safe
def opening_detail(request, pk):
    opening = get_object_or_404(Opening, pk=pk)
    return render(request, "recruiting/opening_detail.html", {"opening": opening})


@staff_required
def home(request):
    return render(request, "recruiting/home.html")


@staff_required
@require_safe
def candidate_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "active")
    if status not in {"active", "archived"}:
        status = "active"
    candidates = Candidate.objects.filter(is_archived=status == "archived")
    if query:
        candidates = candidates.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )
    page = Paginator(candidates, 20).get_page(request.GET.get("page"))
    return render(
        request,
        "recruiting/candidate_list.html",
        {"page_obj": page, "query": query, "status": status},
    )


@staff_required
@require_POST
def candidate_archive(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    candidate.is_archived = True
    candidate.save(update_fields=["is_archived"])
    return redirect("recruiting:candidate_detail", pk=candidate.pk)


@staff_required
@require_POST
def candidate_restore(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    candidate.is_archived = False
    candidate.save(update_fields=["is_archived"])
    return redirect("recruiting:candidate_detail", pk=candidate.pk)


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
