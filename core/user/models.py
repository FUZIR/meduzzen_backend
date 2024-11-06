from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils.models import TimeStampedModel


# Create your models here.
class CustomUser(AbstractUser, TimeStampedModel):
    image_path = models.URLField(blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password", "image_path"]
