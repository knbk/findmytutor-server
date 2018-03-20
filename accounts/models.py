from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    STUDENT = 'student'
    TUTOR = 'tutor'
    TYPES = [
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
    ]
    type = models.CharField(max_length=20, choices=TYPES)

    @property
    def profile(self):
        if self.type == self.STUDENT:
            return self.student
        elif self.type == self.TUTOR:
            return self.tutor
        return None


class Profile(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='%(class)s')
    locations = models.ManyToManyField('accounts.Location', related_name='%(class)s+')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user}"


class Student(Profile):
    tutors = models.ManyToManyField('accounts.Tutor', related_name='students')
    
    def __str__(self):
        return f"{self.user}"


class Tutor(Profile):
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available = models.BooleanField(blank=True, default=True)

    def __str__(self):
        return f"{self.user}"


class Location(models.Model):
    city = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    # location = models.MultiPolygonField()

    def __str__(self):
        return f"{self.street_address} {self.zip_code} {self.city}"
