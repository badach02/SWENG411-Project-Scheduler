from django.db import models

# Create your models here.


class account(models.Model): 
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    account_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.username} | {self.password} | {self.account_type}"