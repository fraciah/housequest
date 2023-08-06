from django.db import models
from account.models import User

# Create your models here.
class ListingType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class ListingItem(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_type = models.ForeignKey(ListingType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    vacancies = models.IntegerField()
    is_available = models.BooleanField(default=True)
    image = models.ImageField()
    booking_fee = models.IntegerField()
    features = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    booked_by = models.ManyToManyField(User, related_name='booked_listings', blank=True)
    rented_by = models.ManyToManyField(User, related_name='rented_listings', blank=True)

    def __str__(self):
        return self.name
    
    def display_date(self):
        if self.created_at == self.updated_at:
            return self.created_at
        else:
            return self.updated_at
    
    @property
    def landlord_username(self):
        return self.landlord.username
    
    
    
    
    
