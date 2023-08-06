# Generated by Django 4.0.3 on 2023-07-04 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_remove_booking_username_booking_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='user',
        ),
        migrations.AddField(
            model_name='booking',
            name='username',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
