# Generated by Django 4.0.2 on 2022-02-16 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "ddns_clienter_core",
            "0003_rewrite_check_and_update_squashed_0005_rename_update_success_task_last_update_success",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="allow_loopback",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="address",
            name="allow_private",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
