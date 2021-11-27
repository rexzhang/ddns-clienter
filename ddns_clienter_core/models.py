from django.db import models


class Status(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()


class Address(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    provider = models.CharField(max_length=255)
    parameter = models.TextField()

    ipv4 = models.BooleanField()
    ipv6 = models.BooleanField()
    ipv4_match_rule = models.TextField(blank=True)
    ipv6_match_rule = models.TextField(blank=True)

    ipv4_address = models.CharField(max_length=15, blank=True)
    ipv4_last_address = models.CharField(max_length=15, blank=True)
    ipv4_last_change_time = models.DateTimeField(blank=True)

    ipv6_address = models.CharField(max_length=45, blank=True)
    ipv6_last_address = models.CharField(max_length=45, blank=True)
    ipv6_last_change_time = models.DateTimeField(blank=True)


class Domain(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    domain = models.CharField(max_length=255)
    host = models.CharField(max_length=255)

    provider = models.CharField(max_length=255)
    provider_token = models.TextField()

    address_name = models.CharField(max_length=255)

    ipv4 = models.BooleanField()
    ipv4_up_to_date = models.BooleanField(blank=True)
    ipv4_last_update_time = models.DateTimeField(blank=True)

    ipv6 = models.BooleanField()
    ipv6_up_to_date = models.BooleanField(blank=True)
    ipv6_last_update_time = models.DateTimeField(blank=True)
