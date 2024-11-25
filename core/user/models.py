from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils.models import TimeStampedModel


# Create your models here.
class CustomUser(AbstractUser, TimeStampedModel):
    image_path = models.URLField(blank=True)
    email = models.EmailField(unique=True)
    company = models.ForeignKey('company.Company', on_delete=models.SET_NULL, null=True, related_name='members')
    description = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=50, blank=True)
    visible = models.BooleanField(default=True, blank=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    class Meta:
        db_table = "users"
