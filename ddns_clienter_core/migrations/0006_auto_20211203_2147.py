# Generated by Django 3.2.9 on 2021-12-03 13:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("ddns_clienter_core", "0005_alter_event_level"),
    ]

    operations = [
        migrations.RenameField(
            model_name="domain",
            old_name="ip_addresses_is_up_to_date",
            new_name="last_update_is_success",
        ),
        migrations.AddField(
            model_name="domain",
            name="last_update_time",
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
