# Generated by Django 4.0.3 on 2023-05-15 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listing', '0002_listingitem_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingitem',
            name='booking_fee',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='listingitem',
            name='features',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
