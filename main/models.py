from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from datetime import date, time, datetime
from main import request_types, ROLES, default_week

def current_time():
    return datetime.now().time()

def current_datetime():
    return datetime.now()

class Account(AbstractUser):
    account_type = models.CharField(max_length=20)
    validate = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        # Automatically validate superusers
        if self.is_superuser:
            self.validate = True

        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username} | {self.account_type} | Validated: {self.validate}"

class RegistrationRequest(models.Model):
    employee = models.ForeignKey(Account, on_delete=models.CASCADE)
    request_date = models.DateField(default=date.today)
    pending = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Registration request for {self.employee.username}"
    
class Notification(models.Model):
    date = models.DateTimeField(default=current_time)
    notif_text = models.CharField(max_length=255)
    employee = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notification for {self.employee.username} sent on {self.date}"
    
class Availability(models.Model):
    employee = models.OneToOneField(Account, on_delete=models.CASCADE)
    week = models.JSONField(default=default_week)

    def __str__(self):
        return f"Availability for {self.employee.username}"

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
    
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    hours_per_week = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def initials(self):
        return (self.first_name[:1] + self.last_name[:1]).upper()
