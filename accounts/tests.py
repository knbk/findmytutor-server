import datetime
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Profile, Student, Tutor, User


class AccountsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test_user', 'test_user@example.com')
        cls.student = User.objects.create_user('student', 'student@example.com')
        student_profile = Profile.objects.create(
            user=cls.student, type=Profile.STUDENT,
            date_of_birth=datetime.date(1999, 12, 31), gender='Male',
        )
        student = Student.objects.create(profile=student_profile)
        cls.tutor = User.objects.create_user('tutor', 'tutor@example.com')
        tutor_profile = Profile.objects.create(
            user=cls.tutor, type=Profile.TUTOR,
            date_of_birth=datetime.date(1999, 12, 31), gender='Female',
        )
        tutor = Tutor.objects.create(
            profile=tutor_profile, hourly_rate='35.00', available=True,
        )

    def test_root_api_view(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test_list_users(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)

    def test_list_students(self):
        response = self.client.get(reverse('student-list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        student = data[0]
        self.assertEqual(student['username'], 'student')
        self.assertEqual(student['date_of_birth'], '1999-12-31')
        self.assertEqual(student['gender'], 'Male')
        self.assertEqual(student['tutors'], [])
        self.assertEqual(student['locations'], [])

    def test_list_tutors(self):
        response = self.client.get(reverse('tutor-list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        tutor = data[0]
        self.assertEqual(tutor['username'], 'tutor')
        self.assertEqual(tutor['date_of_birth'], '1999-12-31')
        self.assertEqual(tutor['gender'], 'Female')
        self.assertEqual(tutor['students'], [])
        self.assertEqual(tutor['location'], None)

    def test_create_student(self):
        data = {
            'username': 'test_user',
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
        }
        response = self.client.post(reverse('student-list'), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertQuerysetEqual(
            Profile.objects.filter(user__username='test_user'),
            [
                '<Profile: test_user>',
            ]
        )
        profile = Profile.objects.get(user__username='test_user')
        self.assertEqual(profile.type, Profile.STUDENT)
        self.assertEqual(profile.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(profile.gender, 'Male')

    def test_update_student(self):
        profile = Profile.objects.create(user=self.user, type=Profile.STUDENT)
        student = Student.objects.create(profile=profile)
        data = {
            'username': 'test_user',
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
        }
        response = self.client.put(reverse('student-detail', kwargs={'pk': student.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.type, Profile.STUDENT)
        self.assertEqual(profile.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(profile.gender, 'Male')

    def test_create_tutor(self):
        data = {
            'username': 'test_user',
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
            'hourly_rate': '35.00',
            'available': 'false',
        }
        response = self.client.post(reverse('tutor-list'), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertQuerysetEqual(
            Profile.objects.filter(user__username='test_user'),
            [
                '<Profile: test_user>',
            ]
        )
        profile = Profile.objects.get(user__username='test_user')
        self.assertEqual(profile.type, 'tutor')
        self.assertEqual(profile.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(profile.gender, 'Male')
        tutor = profile.tutor
        self.assertEqual(tutor.hourly_rate, Decimal('35.00'))
        self.assertFalse(tutor.available)

    def test_update_tutor(self):
        profile = Profile.objects.create(user=self.user, type=Profile.TUTOR)
        tutor = Tutor.objects.create(profile=profile, hourly_rate='0.00', available=False)
        data = {
            'username': 'test_user',
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
            'hourly_rate': '35.00',
            'available': 'true',
        }
        response = self.client.put(reverse('tutor-detail', kwargs={'pk': tutor.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.type, Profile.TUTOR)
        self.assertEqual(profile.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(profile.gender, 'Male')
        tutor.refresh_from_db()
        self.assertEqual(tutor.hourly_rate, Decimal('35.00'))
        self.assertEqual(tutor.available, True)
