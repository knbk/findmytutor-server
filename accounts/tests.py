import datetime
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from .models import Profile, Student, Tutor, User


class AccountsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.new_student = User.objects.create_user('new_student', 'new_student@example.com')
        cls.new_tutor = User.objects.create_user('new_tutor', 'new_tutor@example.com')
        cls.student = User.objects.create_user('student', 'student@example.com', type=User.STUDENT)
        Student.objects.create(
            user=cls.student, date_of_birth=datetime.date(1999, 12, 31), gender='Male',
        )
        cls.tutor = User.objects.create_user('tutor', 'tutor@example.com', type=User.TUTOR)
        tutor = Tutor.objects.create(
            user=cls.tutor, date_of_birth=datetime.date(1999, 12, 31), gender='Female',
            hourly_rate='35.00', available=True, level=Tutor.MASTER, subjects=['App Development'],
        )
        tutor.locations.create(
            city='Eindhoven',
            street_address='Juliusstraat 58',
            zip_code='5621GE',
            longitude=5.4697225,
            latitude=51.441642,
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
        self.assertEqual(len(tutor['locations']), 1)

    def test_create_student(self):
        data = {
            'username': 'new_student',
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
        }
        client = APIClient()
        client.force_authenticate(user=self.new_student)
        response = client.post(reverse('student-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertQuerysetEqual(
            Student.objects.filter(user_id=self.new_student.pk),
            [
                '<Student: new_student>',
            ]
        )
        student = Student.objects.get(user_id=self.new_student.pk)
        self.assertEqual(student.user.type, User.STUDENT)
        self.assertEqual(student.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(student.gender, 'Male')

    def test_update_student(self):
        user = self.student
        student = user.student
        data = {
            'username': 'updated_student',
            'date_of_birth': '1994-12-31',
            'gender': 'Female',
        }
        client = APIClient()
        client.force_authenticate(user=self.student)
        response = client.put(reverse('student-detail', kwargs={'pk': student.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.username, 'updated_student')
        student = user.student
        self.assertEqual(student.date_of_birth, datetime.date(1994, 12, 31))
        self.assertEqual(student.gender, 'Female')

    def test_create_tutor(self):
        data = {
            'username': 'new_tutor',
            'date_of_birth': '1999-12-31',
            'gender': 'Male',
            'hourly_rate': '35.00',
            'level': Tutor.MASTER,
            'subjects': [
                'App Development',
                'Applied Physics',
            ],
            'available': 'false',
        }
        client = APIClient()
        client.force_authenticate(user=self.new_tutor)
        response = client.post(reverse('tutor-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertQuerysetEqual(
            Tutor.objects.filter(user_id=self.new_tutor.pk),
            [
                '<Tutor: new_tutor>',
            ]
        )
        tutor = Tutor.objects.get(user_id=self.new_tutor.pk)
        self.assertEqual(tutor.user.type, User.TUTOR)
        self.assertEqual(tutor.date_of_birth, datetime.date(1999, 12, 31))
        self.assertEqual(tutor.gender, 'Male')
        self.assertEqual(tutor.hourly_rate, Decimal('35.00'))
        self.assertEqual(tutor.level, Tutor.MASTER)
        self.assertListEqual(tutor.subjects, [
            'App Development',
            'Applied Physics',
        ])
        self.assertFalse(tutor.available)

    def test_update_tutor(self):
        user = self.tutor
        tutor = user.tutor
        data = {
            'username': 'updated_tutor',
            'date_of_birth': '1994-12-31',
            'gender': 'Male',
            'hourly_rate': '45.00',
            'available': 'false',
            'level': Tutor.BACHELOR,
            'subjects': [
                'App Development',
                'Applied Physics',
            ],
        }
        client = APIClient()
        client.force_authenticate(user=self.tutor)
        response = client.put(reverse('tutor-detail', kwargs={'pk': tutor.pk}), data=data, format='json')
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.type, User.TUTOR)
        self.assertEqual(user.username, 'updated_tutor')
        tutor = user.tutor
        self.assertEqual(tutor.date_of_birth, datetime.date(1994, 12, 31))
        self.assertEqual(tutor.gender, 'Male')
        self.assertEqual(tutor.hourly_rate, Decimal('45.00'))
        self.assertEqual(tutor.level, Tutor.BACHELOR)
        self.assertListEqual(tutor.subjects, [
            'App Development',
            'Applied Physics',
        ])
        self.assertEqual(tutor.available, False)

    def test_add_to_my_tutors(self):
        student = self.student.student
        tutor = self.tutor.tutor
        client = APIClient()
        client.force_authenticate(user=self.student)
        response = client.post(reverse('tutor-my-tutors', kwargs={'pk': tutor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            student.tutors.all(),
            [
                '<Tutor: tutor>',
            ]
        )
        response = client.delete(reverse('tutor-my-tutors', kwargs={'pk': tutor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            student.tutors.all(),
            []
        )

    def test_filter_tutors(self):
        data = {
            'hourly_rate': '45.00',
            'subject': 'App Development',
            'level': Tutor.MASTER,
            'location': "5.459355,51.454387",
        }
        response = self.client.get(reverse('tutor-search'), data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertEqual(len(json), 1)
        data['location'] = "4.899651,52.377687"
        response = self.client.get(reverse('tutor-search'), data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertEqual(len(json), 0)

    def test_get_profile(self):
        client = APIClient()
        client.force_authenticate(user=self.student)
        response = client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'student')
        self.assertEqual(data['type'], 'student')
