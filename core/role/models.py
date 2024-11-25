
from django.db import models

from core.company.models import Company
from core.user.models import CustomUser
from core.utils.models import TimeStampedModel


# Create your models here.
class UserRoles(models.TextChoices):
    OWNER = ("OW", "Owner")
    ADMIN = ("AD", "Admin")
    MEMBER = ("ME", "Member")


class RoleModel(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=False)
    role = models.CharField(choices=UserRoles.choices, default=UserRoles.MEMBER, blank=False)

    class Meta:
        db_table = "roles"
        unique_together = ("user", "company")

    def __str__(self):
        return f"{self.user} has role {self.role} in {self.company} company"
