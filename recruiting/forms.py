from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Application, Candidate, Opening


class ApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["candidate"].queryset = Candidate.objects.filter(is_archived=False)
        self.fields["opening"].queryset = Opening.objects.filter(
            status=Opening.Status.OPEN
        )
        self.fields["candidate"].error_messages["invalid_choice"] = (
            "Select an existing active candidate. "
            "Archived candidates cannot receive new applications."
        )
        self.fields["opening"].error_messages["invalid_choice"] = (
            "Select an existing open opening. "
            "Closed openings cannot receive new applications."
        )
        self.fields["candidate"].label_from_instance = lambda candidate: (
            f"{candidate.name} ({candidate.email})"
        )
        self.fields["opening"].label_from_instance = lambda opening: (
            f"{opening.title} (#{opening.pk})"
        )

    class Meta:
        model = Application
        fields = ["candidate", "opening"]
        widgets = {
            "candidate": forms.Select(attrs={"class": "select w-full"}),
            "opening": forms.Select(attrs={"class": "select w-full"}),
        }


class OpeningForm(forms.ModelForm):
    class Meta:
        model = Opening
        fields = ["title", "description", "status", "skills"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input w-full"}),
            "description": forms.Textarea(
                attrs={"class": "textarea w-full", "rows": 6}
            ),
            "status": forms.Select(attrs={"class": "select w-full"}),
            "skills": forms.SelectMultiple(attrs={"class": "select w-full", "size": 6}),
        }


class CandidateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "textarea w-full", "rows": 6})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "select w-full"
            else:
                field.widget.attrs["class"] = "input w-full"

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    class Meta:
        model = Candidate
        fields = [
            "name",
            "email",
            "recruitment_source",
            "phone",
            "source_details",
            "notes",
        ]


class StaffAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input w-full"

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                "Sign-in is available to staff accounts only.", code="staff_required"
            )
