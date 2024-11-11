from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import SET_NULL

from core.company.models import Company
from core.utils.models import TimeStampedModel


# Create your models here.
class CustomUser(AbstractUser, TimeStampedModel):
    image_path = models.URLField(blank=True)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, on_delete=SET_NULL, null=True, related_name='members')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password", "image_path"]

    class Meta:
        db_table = "users"
