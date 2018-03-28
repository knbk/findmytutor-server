from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


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
    locations = models.ManyToManyField('accounts.Location', related_name='%(class)ss')
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
    HIGH_SCHOOL = "HIGH_SCHOOL"
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    PHD = "PHD"

    LEVEL_CHOICES = [
        (HIGH_SCHOOL, "High school"),
        (BACHELOR, "Bachelor"),
        (MASTER, "Master"),
        (PHD, "PhD"),
    ]

    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    subjects = ArrayField(models.CharField(max_length=100), default=list)
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES)
    available = models.BooleanField(blank=True, default=True)

    def __str__(self):
        return f"{self.user}"


class Location(models.Model):
    city = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.PointField(geography=True)

    def save(self, *args, **kwargs):
        self.location = Point(self.longitude, self.latitude, srid=4326)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.street_address} {self.zip_code} {self.city}"
