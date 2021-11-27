# Generated by Django 3.2.9 on 2021-11-27 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("provider", models.CharField(max_length=255)),
                ("parameter", models.TextField()),
                ("ipv4", models.BooleanField()),
                ("ipv6", models.BooleanField()),
                ("ipv4_match_rule", models.TextField()),
                ("ipv6_match_rule", models.TextField()),
                ("ipv4_address", models.CharField(max_length=15)),
                ("ipv6_address", models.CharField(max_length=45)),
                ("ipv4_address_last", models.CharField(max_length=15)),
                ("ipv6_address_last", models.CharField(max_length=45)),
                ("ipv4_last_change_time", models.DateTimeField()),
                ("ipv6_last_change_time", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Domain",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("domain", models.CharField(max_length=255)),
                ("host", models.CharField(max_length=255)),
                ("provider", models.CharField(max_length=255)),
                ("provider_token", models.TextField()),
                ("address_name", models.CharField(max_length=255)),
                ("ipv4", models.BooleanField()),
                ("ipv4_up_to_date", models.BooleanField()),
                ("ipv4_last_update_time", models.DateTimeField()),
                ("ipv6", models.BooleanField()),
                ("ipv6_up_to_date", models.BooleanField()),
                ("ipv6_last_update_time", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Status",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.CharField(max_length=255)),
                ("value", models.TextField()),
            ],
        ),
    ]
