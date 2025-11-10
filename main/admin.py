from django.contrib import admin
from .models import account, shift, time_off

# Register your models here.    

admin.site.register(account)
admin.site.register(shift)
admin.site.register(time_off)
