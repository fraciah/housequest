# Generated by Django 4.0.3 on 2023-07-10 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('listing', '0009_alter_listingitem_booking_fee'),
        ('payment', '0010_remove_booking_user_booking_booking_tenant'),
    ]

    operations = [
        migrations.CreateModel(
            name='Renting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('renting_tenant', models.CharField(max_length=255)),
                ('transaction_code', models.CharField(max_length=255)),
                ('tenant_phone_number', models.CharField(max_length=255)),
                ('transaction_date', models.DateTimeField()),
                ('amount_paid', models.IntegerField()),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='listing.listingitem')),
            ],
        ),
    ]