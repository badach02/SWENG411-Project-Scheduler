from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from datetime import date, time

ROLES = [
    ("MGR", "Manager"),
    ("CK", "Cook"),
    ("SVR", "Server"),
]

class account(AbstractUser):
    account_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.username} | {self.account_type}"
    
class shift(models.Model):
    date = models.DateField(default=date.today)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    role = models.CharField(choices=ROLES, default="SVR")
    employee = models.ForeignKey(account, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        emp_name = self.employee.username if self.employee else "Unassigned"
        return f"{self.date} {self.start_time}-{self.end_time} ({self.role}) - {emp_name}"

    
class time_off(models.Model):
    date = models.DateField(default=date.today)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    employee = models.ForeignKey(account, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        emp_name = self.employee.first_name if self.employee else "No employee"
        return f"Time off {self.date} {self.start_time}-{self.end_time} by {emp_name}"

