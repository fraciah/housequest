# Generated by Django 4.0.3 on 2023-07-03 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payment', '0003_delete_booking'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listing_name', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('transaction_code', models.CharField(max_length=255)),
                ('tenant_phone_number', models.CharField(max_length=255)),
                ('transaction_date', models.DateTimeField()),
                ('amount_paid', models.IntegerField()),
            ],
        ),
    ]
