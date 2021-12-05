from django.db import models

from ddns_clienter_core.runtimes.event import EventLevel


class Address(models.Model):
    # from config
    name = models.CharField(max_length=255, primary_key=True)

    provider = models.CharField(max_length=255)
    parameter = models.TextField()

    ipv4 = models.BooleanField()
    ipv6 = models.BooleanField()
    ipv4_match_rule = models.TextField()
    ipv6_match_rule = models.TextField()

    # from address provider
    ipv4_address = models.CharField(max_length=15, null=True)
    ipv4_last_address = models.CharField(max_length=15, null=True)
    ipv4_last_change_time = models.DateTimeField(null=True)

    ipv6_address = models.CharField(max_length=45, null=True)
    ipv6_last_address = models.CharField(max_length=45, null=True)
    ipv6_last_change_time = models.DateTimeField(null=True)

    # record's last update datetime
    time = models.DateTimeField(auto_now=True)


class Task(models.Model):
    # from config
    name = models.CharField(max_length=255, primary_key=True)

    provider = models.CharField(max_length=255)
    provider_token = models.TextField()

    domain = models.CharField(max_length=255)
    host = models.CharField(max_length=255)

    address_name = models.CharField(max_length=255)
    ipv4 = models.BooleanField()
    ipv6 = models.BooleanField()

    # from Dynamic DNS provider's response
    ip_addresses = models.CharField(max_length=62)
    last_ip_addresses = models.TextField(max_length=62, null=True)
    last_update_is_success = models.BooleanField()
    last_update_time = models.DateTimeField(null=True)

    # last run task timestamp
    time = models.DateTimeField(auto_now=True)


class Status(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()


class Event(models.Model):
    level = models.TextField(choices=EventLevel.choices)
    message = models.TextField()

    # timestamp
    time = models.DateTimeField(auto_now=True)
