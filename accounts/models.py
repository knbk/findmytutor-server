from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Profile(models.Model):
    STUDENT = 'student'
    TUTOR = 'tutor'
    TYPES = [
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
    ]
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPES)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user}"


class Student(models.Model):
    profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE)
    tutors = models.ManyToManyField('accounts.Tutor', related_name='students')
    locations = models.ManyToManyField('accounts.Location', related_name='students+')

    def __str__(self):
        return f"{self.profile}"


class Tutor(models.Model):
    profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE)
    location = models.ForeignKey('accounts.Location', on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name='tutors+')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(blank=True)

    def __str__(self):
        return f"{self.profile}"


class Location(models.Model):
    city = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    # location = models.MultiPolygonField()

    def __str__(self):
        return f"{self.street_address} {self.zip_code} {self.city}"
