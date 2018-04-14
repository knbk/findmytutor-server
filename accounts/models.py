import datetime

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


class ProfilePicture(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='picture')
    image = models.BinaryField()


class Profile(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='%(class)s')
    locations = models.ManyToManyField('accounts.Location', related_name='%(class)ss')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True)

    @property
    def date_of_birth_datetime(self):
        return datetime.datetime.combine(self.date_of_birth, datetime.datetime.min.time())

    @date_of_birth_datetime.setter
    def date_of_birth_datetime(self, date_of_birth):
        self.date_of_birth = date_of_birth.date()

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
    subjects = ArrayField(
        ArrayField(
            models.CharField(max_length=100),
            size=2,
            default=list,
        ),
        default=list,
    )
    available = models.BooleanField(blank=True, default=True)

    @property
    def subject_dicts(self):
        return list(map(
            lambda subject: {'subject': subject[0], 'level': subject[1]},
            self.subjects,
        ))

    @subject_dicts.setter
    def subject_dicts(self, subject_dicts):
        self.subjects = list(map(
            lambda subject: [subject['subject'], subject['level']],
            subject_dicts,
        ))

    def __str__(self):
        return f"{self.user}"


class Location(models.Model):
    address = models.CharField(max_length=255)
    google_id = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.PointField(geography=True)

    def save(self, *args, **kwargs):
        self.location = Point(self.longitude, self.latitude, srid=4326)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address}"
