# Generated by Django 4.0.3 on 2023-06-19 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_paybill_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='paybill_number',
        ),
    ]