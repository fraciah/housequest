from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    is_admin = models.BooleanField('Is admin', default=False)
    is_tenant = models.BooleanField('Is tenant', default=False)
    is_landlord = models.BooleanField('Is landlord', default=False)
    phone_number = models.CharField(max_length=10)