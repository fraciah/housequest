from django.contrib import admin
from .models import ListingType, ListingItem
# Register your models here.

admin.site.register(ListingType)
admin.site.register(ListingItem)
