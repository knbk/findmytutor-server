import datetime
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Profile, Student, Tutor, User


class AccountsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test_user', 'test_user@example.com')
        cls.student = User.objects.create_user('student', 'student@example.com', type=User.STUDENT)
        Student.objects.create(
            user=cls.student, date_of_birth=datetime.date(1999, 12, 31), gender='Male',
        )
        cls.tutor = User.objects.create_user('tutor', 'tutor@example.com', type=User.TUTOR)
        Tutor.objects.create(
            user=cls.tutor, date_of_birth=datetime.date(1999, 12, 31), gender='Female',
            hourly_rate='35.00', available=True,
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
        self.assertEqual(tutor['locations'], [])

    def test_create_student(self):
        data = {
            'user': self.user.id,
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
        }
        response = self.client.post(reverse('student-list'), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertQuerysetEqual(
            Student.objects.filter(user__username='test_user'),
            [
                '<Student: test_user>',
            ]
        )
        student = Student.objects.get(user__username='test_user')
        self.assertEqual(student.user.type, User.STUDENT)
        self.assertEqual(student.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(student.gender, 'Male')

    def test_update_student(self):
        user = self.student
        student = user.student
        data = {
            'user': user.pk,
            'date_of_birth': '1994-12-31',
            'gender': 'Female',
        }
        response = self.client.put(reverse('student-detail', kwargs={'pk': student.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertEqual(student.date_of_birth, datetime.date(1994, 12, 31))
        self.assertEqual(student.gender, 'Female')

    def test_create_tutor(self):
        data = {
            'user': self.user.pk,
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
            'hourly_rate': '35.00',
            'available': 'false',
        }
        response = self.client.post(reverse('tutor-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertQuerysetEqual(
            Tutor.objects.filter(user__username='test_user'),
            [
                '<Tutor: test_user>',
            ]
        )
        user = User.objects.get(username='test_user')
        self.assertEqual(user.type, User.TUTOR)
        tutor = user.tutor
        self.assertEqual(tutor.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(tutor.gender, 'Male')
        self.assertEqual(tutor.hourly_rate, Decimal('35.00'))
        self.assertFalse(tutor.available)

    def test_update_tutor(self):
        user = self.tutor
        tutor = user.tutor
        data = {
            'user': user.pk,
            'date_of_birth': '1994-12-31',
            'gender': 'Male',
            'hourly_rate': '45.00',
            'available': 'false',
        }
        response = self.client.put(reverse('tutor-detail', kwargs={'pk': tutor.pk}), data=data, format='json')
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='tutor')
        self.assertEqual(user.type, User.TUTOR)
        tutor.refresh_from_db()
        self.assertEqual(tutor.date_of_birth, datetime.date(1994, 12, 31))
        self.assertEqual(tutor.gender, 'Male')
        self.assertEqual(tutor.hourly_rate, Decimal('45.00'))
        self.assertEqual(tutor.available, False)
