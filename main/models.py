from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from datetime import date, time, datetime

ROLES = [
    ("MGR", "Manager"),
    ("CK", "Cook"),
    ("SVR", "Server"),
]

def current_time():
    return datetime.now().time()

class Account(AbstractUser):
    account_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.username} | {self.account_type}"
    
class Request(models.Model):
    date = models.DateField(default=date.today)
    start_time = models.TimeField(default=current_time)
    end_time = models.TimeField(default=current_time)

    class Meta:
        abstract = True 
    
class Shift(Request, models.Model):
    role = models.CharField(choices=ROLES, default="SVR")
    employee = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        emp_name = self.employee.username if self.employee else "Unassigned"
        return f"{self.date} {self.start_time}-{self.end_time} ({self.role}) - {emp_name}"

    
class TimeOff(Request, models.Model):
    employee = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        emp_name = self.employee.first_name if self.employee else "No employee"
        return f"Time off {self.date} {self.start_time}-{self.end_time} by {emp_name}"

