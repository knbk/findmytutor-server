import datetime

from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Profile, User, Student


class AccountsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('marten', 'marten.knbk@gmail.com')

    def test_root_api_view(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test_list_students(self):
        response = self.client.get(reverse('student-list'))
        self.assertEqual(response.status_code, 200)

    def test_list_users(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)

    def test_create_student(self):
        data = {
            'username': 'marten',
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
        }
        response = self.client.post(reverse('student-list'), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertQuerysetEqual(
            Profile.objects.filter(user__username='marten'),
            [
                '<Profile: marten>',
            ]
        )
        profile = Profile.objects.get(user__username='marten')
        self.assertEqual(profile.type, 'student')
        self.assertEqual(profile.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(profile.gender, 'Male')

    def test_update_student(self):
        profile = Profile.objects.create(user=self.user, type='student')
        student = Student.objects.create(profile=profile)
        data = {
            'username': 'marten',
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
        }
        response = self.client.put(reverse('student-detail', kwargs={'pk': student.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.type, 'student')
        self.assertEqual(profile.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(profile.gender, 'Male')
