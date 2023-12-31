# Generated by Django 4.0.3 on 2023-07-12 15:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('listing', '0010_alter_listingitem_booking_fee_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingitem',
            name='rented_by',
            field=models.ManyToManyField(blank=True, related_name='rented_listings', to=settings.AUTH_USER_MODEL),
        ),
    ]
