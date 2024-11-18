from django.db import models

from core.company.models import Company
from core.user.models import CustomUser
from core.utils.models import TimeStampedModel


class Status(models.TextChoices):
    PENDING = 'PD', 'Pending'
    ACCEPTED = 'AC', 'Accepted'
    REVOKED = 'RV', 'Revoked'
    REJECTED = 'RJ', 'Rejected'


# Create your models here.
class InvitationModel(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, related_name="invitations")
    status = models.CharField(choices=Status.choices, default=Status.PENDING, blank=False)

    class Meta:
        db_table = "invitations"

    def __str__(self):
        return f"{self.company.name} send invitation to {self.user}. Status: {self.status}"


class RequestModel(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, related_name="requests_from_user")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, related_name="requests")
    status = models.CharField(choices=Status.choices, default=Status.PENDING, blank=False)

    class Meta:
        db_table = "requests"

    def __str__(self):
        return f"{self.user} send request to join {self.company}. Status: {self.status}"
