from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from .decorators import staff_required
from .forms import ApplicationForm, ApplicationStageForm, CandidateForm, OpeningForm
from .models import Application, Candidate, Opening


@staff_required
@require_POST
def application_stage(request, pk):
    application = get_object_or_404(Application, pk=pk)
    form = ApplicationStageForm(request.POST)
    if form.is_valid():
        application.stage = form.cleaned_data["stage"]
        application.save(update_fields=["stage"])
        feedback = f"Stage updated to {application.get_stage_display()}."
    else:
        feedback = "Stage was not changed. Select a valid stage."
    return render(
        request,
        "recruiting/partials/pipeline_results.html",
        {
            **_pipeline_context(request),
            "feedback": feedback,
            "stage_error": not form.is_valid(),
        },
    )


@staff_required
@require_safe
def application_list(request):
    return render(
        request, "recruiting/application_list.html", _pipeline_context(request)
    )


def _pipeline_context(request):
    query = request.GET.get("q", "").strip()
    opening = request.GET.get("opening", "")
    openings = Opening.objects.all()
    if opening not in {str(pk) for pk in openings.values_list("pk", flat=True)}:
        opening = ""
    stage = request.GET.get("stage", "")
    if stage not in Application.Stage.values:
        stage = ""
    applications = Application.objects.select_related("candidate", "opening")
    if query:
        applications = applications.filter(
            Q(candidate__name__icontains=query) | Q(candidate__email__icontains=query)
        )
    if opening:
        applications = applications.filter(opening_id=opening)
    if stage:
        applications = applications.filter(stage=stage)
    return {
        "applications": applications,
        "query": query,
        "opening_filter": opening,
        "stage": stage,
        "openings": openings,
        "stages": Application.Stage.choices,
    }


@staff_required
@require_http_methods(["GET", "POST"])
def application_create(request):
    initial = {}
    for field, model in [("candidate", Candidate), ("opening", Opening)]:
        if request.GET.get(field):
            try:
                initial[field] = get_object_or_404(model, pk=int(request.GET[field]))
            except ValueError, OverflowError:
                raise Http404("Record not found") from None
    form = ApplicationForm(
        request.POST if request.method == "POST" else None, initial=initial
    )
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                application = form.save()
        except IntegrityError:
            if not Application.objects.filter(
                candidate=form.cleaned_data["candidate"],
                opening=form.cleaned_data["opening"],
            ).exists():
                raise
            form.add_error(
                None, "An application for this candidate and opening already exists."
            )
        else:
            if "opening" in initial and "candidate" not in initial:
                return redirect("recruiting:opening_detail", pk=application.opening_id)
            return redirect("recruiting:candidate_detail", pk=application.candidate_id)
    return render(
        request, "recruiting/application_form.html", {"form": form, **initial}
    )


@staff_required
@require_safe
def opening_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all")
    if status not in {"all", *Opening.Status.values}:
        status = "all"
    openings = Opening.objects.all()
    if query:
        openings = openings.filter(title__icontains=query)
    if status != "all":
        openings = openings.filter(status=status)
    page = Paginator(openings, 20).get_page(request.GET.get("page"))
    return render(
        request,
        "recruiting/opening_list.html",
        {"page_obj": page, "query": query, "status": status},
    )


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
    return render(
        request,
        "recruiting/opening_detail.html",
        {
            "opening": opening,
            "applications": opening.applications.select_related("candidate"),
        },
    )


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
    return render(
        request,
        "recruiting/candidate_detail.html",
        {
            "candidate": candidate,
            "applications": candidate.applications.select_related("opening"),
        },
    )


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
