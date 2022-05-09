from django.contrib.auth.models import User
from django.db import models

class Record(models.Model):
    name = models.CharField(null=True, default='', max_length=64)
    json = models.JSONField(null=True)
    error = models.CharField(null=True, max_length=256)
    isloaded = models.BooleanField(default=False)
    user = models.ForeignKey(User, default='1', on_delete=models.CASCADE)
