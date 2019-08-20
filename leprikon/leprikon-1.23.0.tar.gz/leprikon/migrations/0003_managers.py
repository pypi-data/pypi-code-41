# Generated by Django 1.10.7 on 2017-09-04 19:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leprikon', '0002_initial_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_years', models.ManyToManyField(related_name='managers', to='leprikon.SchoolYear', verbose_name='school years')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='leprikon_manager', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ('user__first_name', 'user__last_name'),
                'verbose_name': 'manager',
                'verbose_name_plural': 'managers',
            },
        ),
        migrations.AddField(
            model_name='courselistplugin',
            name='managers',
            field=models.ManyToManyField(blank=True, help_text='Keep empty to skip searching by managers.', related_name='_courselistplugin_managers_+', to='leprikon.Manager', verbose_name='managers'),
        ),
        migrations.AddField(
            model_name='eventlistplugin',
            name='managers',
            field=models.ManyToManyField(blank=True, help_text='Keep empty to skip searching by managers.', related_name='_eventlistplugin_managers_+', to='leprikon.Manager', verbose_name='managers'),
        ),
        migrations.AddField(
            model_name='subject',
            name='managers',
            field=models.ManyToManyField(blank=True, related_name='subjects', to='leprikon.Manager', verbose_name='managers'),
        ),
    ]
