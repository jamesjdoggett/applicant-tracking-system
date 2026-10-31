from django.contrib import admin

from .forms import CandidateForm
from .models import Candidate, Opening, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Opening)
class OpeningAdmin(admin.ModelAdmin):
    list_display = ["title", "status"]


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    form = CandidateForm
    list_display = ["name", "email", "recruitment_source", "is_archived"]
