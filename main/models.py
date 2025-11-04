from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from datetime import date, time

ROLES = {
    "MGR": "Manager",
    "CK": "Cook",
    "SVR": "Server",
}

class account(AbstractUser):
    account_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.username} | {self.account_type}"
    
class shift(models.Model):
    date = models.DateField(default=date.today)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    role = models.CharField(choices=ROLES, default="Server")
    cover_employee_id = models.IntegerField(default=0)

    def __str__(self):
        return f"Shift on {self.date} from {self.start_time} to {self.end_time} doing: {self.role}"
    
