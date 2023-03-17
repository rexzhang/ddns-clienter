from django.db import models

from ddns_clienter_core.constants import EventLevel


class Address(models.Model):
    # from config
    name = models.CharField(max_length=255, primary_key=True)
    enable = models.BooleanField(default=True)

    provider_name = models.CharField(max_length=255)
    provider_parameter = models.TextField()

    ipv4 = models.BooleanField()
    ipv4_match_rule = models.TextField()
    ipv6 = models.BooleanField()
    ipv6_prefix_length = models.IntegerField(null=True)
    ipv6_match_rule = models.TextField()
    allow_private = models.BooleanField()
    allow_loopback = models.BooleanField()

    # from address provider
    ipv4_previous_address = models.CharField(max_length=15, null=True)
    ipv4_last_address = models.CharField(max_length=15, null=True)
    ipv4_last_change_time = models.DateTimeField(null=True)

    ipv6_previous_address = models.CharField(max_length=45, null=True)
    ipv6_last_address = models.CharField(max_length=45, null=True)
    ipv6_last_change_time = models.DateTimeField(null=True)

    # record's last update datetime
    time = models.DateTimeField(auto_now=True)


class Task(models.Model):
    # from config
    name = models.CharField(max_length=255, primary_key=True)
    enable = models.BooleanField(default=True)

    address_name = models.CharField(max_length=255)
    ipv4 = models.BooleanField()
    ipv6 = models.BooleanField()

    provider_name = models.CharField(max_length=255)
    provider_auth = models.TextField()

    domain = models.CharField(max_length=255)
    host = models.CharField(max_length=255)

    # from Dynamic DNS provider's response
    previous_ip_addresses = models.TextField(max_length=62, null=True)
    last_ip_addresses = models.CharField(max_length=62)

    last_update_time = models.DateTimeField(null=True)

    last_update_success = models.BooleanField(default=False)
    last_update_success_time = models.DateTimeField(null=True)

    # record's last update datetime
    time = models.DateTimeField(auto_now=True)


class Status(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()


class Event(models.Model):
    level = models.TextField(choices=EventLevel.choices)
    message = models.TextField()

    # timestamp
    time = models.DateTimeField(auto_now=True)
