from django.db import models
from django.utils import timezone


# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, blank=False)
    updated_at = models.DateTimeField(blank=False)
    class Meta:
        abstract = True