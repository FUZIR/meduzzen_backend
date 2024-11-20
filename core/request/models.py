from django.db import models

from core.company.models import Company
from core.user.models import CustomUser
from core.utils.models import TimeStampedModel

class RequestStatus(models.TextChoices):
    PENDING = 'PD', 'Pending'
    ACCEPTED = 'AC', 'Accepted'
    REJECTED = 'RJ', 'Rejected'
    CANCELED = 'CD', 'Canceled'

# Create your models here.
class RequestModel(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, related_name="requests_from_user")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, related_name="requests")
    status = models.CharField(choices=RequestStatus.choices, default=RequestStatus.PENDING, blank=False)

    class Meta:
        db_table = "requests"

    def __str__(self):
        return f"{self.user} send request to join {self.company}. Status: {self.status}"
