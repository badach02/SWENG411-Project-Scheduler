from django.contrib import admin
from .models import Account, Shift, TimeOff

# Register your models here.    

admin.site.register(Account)
admin.site.register(Shift)
admin.site.register(TimeOff)
