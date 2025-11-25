from django.contrib import admin
from .models import Account, Shift, TimeOff, Notification, Availability

# Register your models here.    

admin.site.register(Account)
admin.site.register(Shift)
admin.site.register(TimeOff)
admin.site.register(Notification)
admin.site.register(Availability)
