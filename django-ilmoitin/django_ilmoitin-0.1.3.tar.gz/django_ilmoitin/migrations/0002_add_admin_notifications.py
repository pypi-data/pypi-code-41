# Generated by Django 2.2.3 on 2019-08-20 11:24

from django.conf import settings
from django.db import migrations, models
import django_ilmoitin.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_ilmoitin", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationtemplate",
            name="admin_notification_subject",
            field=models.CharField(
                blank=True,
                help_text="Subject for admins' notification",
                max_length=200,
                verbose_name="admin notification subject",
            ),
        ),
        migrations.AddField(
            model_name="notificationtemplate",
            name="admin_notification_text",
            field=models.TextField(
                blank=True,
                help_text="Text body for admins' notification.",
                verbose_name="admin notification text",
            ),
        ),
        migrations.AddField(
            model_name="notificationtemplate",
            name="admins_to_notify",
            field=models.ManyToManyField(
                blank=True,
                help_text="Choose admin users you want to be notified when this event happens.",
                related_name="_notificationtemplate_admins_to_notify_+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Admins to notify",
            ),
        ),
        migrations.AddField(
            model_name="notificationtemplate",
            name="from_email",
            field=models.EmailField(
                default=django_ilmoitin.models.get_default_from_email,
                max_length=100,
                verbose_name="From email",
            ),
        ),
    ]
