from django.db import models
from account.models import User
from listing.models import ListingItem

class Booking(models.Model):
    listing = models.ForeignKey(ListingItem, on_delete=models.CASCADE)
    booking_tenant = models.CharField(max_length=255)
    transaction_code = models.CharField(max_length=255)
    tenant_phone_number = models.CharField(max_length=255)
    transaction_date = models.DateTimeField()
    amount_paid = models.IntegerField()

    def __str__(self):
        return f"{self.listing.name} - {self.booking_tenant}" 
    

class Renting(models.Model):
    listing = models.ForeignKey(ListingItem, on_delete=models.CASCADE)
    renting_tenant = models.CharField(max_length=255)
    transaction_code = models.CharField(max_length=255)
    tenant_phone_number = models.CharField(max_length=255)
    transaction_date = models.DateTimeField()
    amount_paid = models.IntegerField()

    def __str__(self):
        return f"{self.listing.name} - {self.renting_tenant}"
