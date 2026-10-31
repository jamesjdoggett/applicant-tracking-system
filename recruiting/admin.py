from django.contrib import admin

from .forms import CandidateForm
from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    form = CandidateForm
    list_display = ["name", "email", "recruitment_source", "is_archived"]
