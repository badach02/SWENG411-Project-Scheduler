from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from datetime import date, time, datetime
from main import request_types, ROLES

def current_time():
    return datetime.now().time()

class Account(AbstractUser):
    account_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.username} | {self.account_type}"
    
class Notification(models.Model):
    date = models.DateTimeField(default=current_time)
    notif_text = models.CharField(max_length=255)
    employee = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notification for {self.employee.username} sent on {self.date}"
    
class Request(models.Model):
    request_date = models.DateField(default=date.today)
    start_time = models.DateTimeField(default=current_time)
    end_time = models.DateTimeField(default=current_time)
    approved = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)

    class Meta:
        abstract = True 
    
class Shift(models.Model):
    date = models.DateField(default=date.today)
    start_time = models.TimeField(default=current_time)
    end_time = models.TimeField(default=current_time)
    role = models.CharField(choices=ROLES, default="SVR")
    employee = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        emp_name = self.employee.username if self.employee else "Unassigned"
        return f"{self.date} {self.start_time}-{self.end_time} ({self.role}) - {emp_name}"

    
class TimeOff(Request, models.Model):
    employee = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(default="Unpaid")
    
    def __str__(self):
        emp_name = self.employee.first_name if self.employee else "No employee"
        return f"Time off {self.request_date} {self.start_time}-{self.end_time} by {emp_name}"
