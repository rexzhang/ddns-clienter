# Generated by Django 3.2.9 on 2021-12-04 07:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ddns_clienter_core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="last_update_time",
            field=models.DateTimeField(null=True),
        ),
    ]
