from django.db import models

from core.user.models import CustomUser
from core.utils.models import TimeStampedModel


# Create your models here.
class NotificationStatus(models.TextChoices):
    ACTIVE = ("AC", "Active")
    READ = ("RD", "Read")


class NotificationModel(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False)
    status = models.CharField(max_length=2, default=NotificationStatus.ACTIVE, choices=NotificationStatus.choices,
                              blank=False)
    text = models.CharField(max_length=255, blank=False)
