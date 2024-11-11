from django.db import models

from core.utils.models import TimeStampedModel


# Create your models here.

class Company(TimeStampedModel):
    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.CharField(max_length=255, blank=False)
    company_email = models.EmailField(blank=False)
    image_path = models.URLField(blank=True)
    owner = models.ForeignKey("user.CustomUser", blank=False, on_delete=models.SET_NULL, null=True,
                              related_name="owned_companies")

    class Meta:
        db_table = "companies"
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self) -> str:
        return f"{self.name} - {self.company_email}"
