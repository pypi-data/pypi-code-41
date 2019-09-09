# -*- coding: utf-8 -*-

"""
Models with CacheManager as model manager to be used for CacheManager integration tests
"""
from django.db import models

from django2_manager_cache import CacheManager


class Manufacturer(models.Model):
    name = models.CharField(max_length=128)

    objects = CacheManager()

    # https://docs.djangoproject.com/en/2.2/topics/db/managers/#base-managers
    class Meta:
        base_manager_name = 'objects'


class Car(models.Model):
    make = models.ForeignKey('Manufacturer', related_name='cars', null=True, on_delete=models.SET_NULL)
    model = models.CharField(max_length=128)
    year = models.IntegerField()
    engine = models.OneToOneField('Engine', on_delete=models.CASCADE)

    objects = CacheManager()

    # https://docs.djangoproject.com/en/2.2/topics/db/managers/#base-managers
    class Meta:
        base_manager_name = 'objects'


class Driver(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    cars = models.ManyToManyField('Car')

    objects = CacheManager()


class Engine(models.Model):
    name = models.CharField(max_length=128)
    horse_power = models.IntegerField()
    torque = models.CharField(max_length=128)

    objects = CacheManager()

    # https://docs.djangoproject.com/en/2.2/topics/db/managers/#base-managers
    class Meta:
        base_manager_name = 'objects'


class Person(models.Model):
    name = models.CharField(max_length=128)

    objects = CacheManager()

    # https://docs.djangoproject.com/en/2.2/topics/db/managers/#base-managers
    class Meta:
        base_manager_name = 'objects'


class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Person, through='Membership', related_name='groups')

    objects = CacheManager()


class Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=64)

    objects = CacheManager()

    # https://docs.djangoproject.com/en/2.2/topics/db/managers/#base-managers
    class Meta:
        base_manager_name = 'objects'
