from django.db import models


class Candidate(models.Model):
    class Source(models.TextChoices):
        COMPANY_WEBSITE = "company_website", "Company website"
        JOB_BOARDS = "job_boards", "Job boards"
        REFERRALS = "referrals", "Referrals"
        OTHER = "other", "Other sources"

    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    recruitment_source = models.CharField(max_length=20, choices=Source.choices)
    phone = models.CharField(max_length=50, blank=True)
    source_details = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)
