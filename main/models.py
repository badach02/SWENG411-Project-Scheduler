from django.contrib.auth.models import AbstractUser
from django.db import models

class account(AbstractUser):
    account_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.username} | {self.account_type}"
    
class shift(models.Model):
    date = models.DateField
    time = models.TimeField
    role = models.CharField(max_length=30)

