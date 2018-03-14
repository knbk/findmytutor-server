from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    date_of_birth = models.DateTimeField(blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True)


class Profile(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)


class Student(models.Model):
    profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE)
    tutors = models.ManyToManyField('accounts.Tutor', related_name='students')
    locations = models.ManyToManyField('accounts.Location', related_name='students+')


class Tutor(models.Model):
    profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE)
    location = models.ForeignKey('accounts.Location', on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name='tutors+')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(blank=True)


class Location(models.Model):
    city = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    # location = models.MultiPolygonField()
