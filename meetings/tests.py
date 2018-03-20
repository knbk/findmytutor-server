import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from accounts.models import User, Student, Tutor
from .models import Meeting, Review


class MeetingsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.new_student = User.objects.create_user('new_student', 'new_student@example.com')
        cls.new_tutor = User.objects.create_user('new_tutor', 'new_tutor@example.com')
        cls.student = User.objects.create_user('student', 'student@example.com', type=User.STUDENT)
        student = Student.objects.create(
            user=cls.student, date_of_birth=datetime.date(1999, 12, 31), gender='Male',
        )
        student.locations.create(
            city='Eindhoven', street_address='Stationsplein 1', zip_code='1234AB', latitude=42.00, longitude=37.00,
        )
        cls.tutor = User.objects.create_user('tutor', 'tutor@example.com', type=User.TUTOR)
        tutor = Tutor.objects.create(
            user=cls.tutor, date_of_birth=datetime.date(1999, 12, 31), gender='Female',
            hourly_rate='35.00', available=True,
        )
        student.tutors.add(tutor)

    def test_create_meeting_as_student(self):
        data = {
            'tutor': self.tutor.tutor.id,
            'student': self.student.student.id,
            'start': '2021-03-05 12:00:00',
            'end': '2021-03-05 13:00:00',
            'location': self.student.profile.locations.first().pk,
        }
        client = APIClient()
        client.force_authenticate(user=self.student)
        response = client.post(reverse('meeting-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        meeting_pk = response.json()['pk']
        meeting = Meeting.objects.get(pk=meeting_pk)

        self.assertEqual(meeting.start, timezone.make_aware(datetime.datetime(2021, 3, 5, 12, 0, 0)))
        self.assertEqual(meeting.end, timezone.make_aware(datetime.datetime(2021, 3, 5, 13, 0, 0)))

        self.assertEqual(meeting.student_id, self.student.student.pk)
        self.assertIsNotNone(meeting.student_accepted_at)
        self.assertIsNone(meeting.student_cancelled_at)

        self.assertEqual(meeting.tutor_id, self.tutor.tutor.pk)
        self.assertIsNone(meeting.tutor_accepted_at)
        self.assertIsNone(meeting.tutor_cancelled_at)
