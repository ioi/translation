from django.db import models
from django.contrib.auth.models import User


class UserTranslationQuota(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    credit = models.PositiveIntegerField(default=0)
    used = models.PositiveIntegerField(default=0)
