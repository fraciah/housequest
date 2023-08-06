from django.contrib import admin

from payment.models import Booking, Renting

# Register your models here.
admin.site.register(Booking)
admin.site.register(Renting)