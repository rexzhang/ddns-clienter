# Generated by Django 3.2.9 on 2021-11-27 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ddns_clienter_core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="domain",
            name="last_ip_addresses",
            field=models.TextField(max_length=62, null=True),
        ),
    ]
