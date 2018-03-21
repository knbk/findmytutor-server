import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from accounts.models import User, Student, Tutor
from .models import Meeting, Review


class MeetingsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
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
        now = timezone.now()
        cls.future_meeting = Meeting.objects.create(
            student=student, tutor=tutor, start=now + datetime.timedelta(days=1),
            end=now + datetime.timedelta(days=1, hours=1),
        )
        cls.past_meeting = Meeting.objects.create(
            student=student, tutor=tutor, start=now - datetime.timedelta(days=1, hours=1),
            end=now - datetime.timedelta(days=1),
        )

    def test_create_invalid_meeting(self):
        student = self.student.profile
        tutor = self.tutor.profile
        student.tutors.add(tutor)
        data = {
            'tutor': tutor.id,
            'student': student.id,
            'start': '2021-03-05 13:00:00',
            'end': '2021-03-05 12:00:00',
            'location': student.locations.first().pk,
        }
        client = APIClient()
        client.force_authenticate(user=self.student)
        response = client.post(reverse('meeting-list'), data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_meeting_as_student(self):
        student = self.student.profile
        tutor = self.tutor.profile
        data = {
            'tutor': tutor.id,
            'student': student.id,
            'start': '2021-03-05 12:00:00',
            'end': '2021-03-05 13:00:00',
            'location': student.locations.first().pk,
        }
        client = APIClient()
        client.force_authenticate(user=self.student)
        response = client.post(reverse('meeting-list'), data=data, format='json')
        self.assertEqual(response.status_code, 403)

        student.tutors.add(tutor)
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

    def test_accept_cancel_meeting(self):
        student = self.student.profile
        tutor = self.tutor.profile
        student.tutors.add(tutor)
        data = {
            'tutor': tutor.id,
            'student': student.id,
            'start': '2021-03-05 12:00:00',
            'end': '2021-03-05 13:00:00',
            'location': student.locations.first().pk,
        }
        client = APIClient()
        client.force_authenticate(user=self.student)
        response = client.post(reverse('meeting-list'), data=data, format='json')
        meeting_pk = response.json()['pk']
        meeting = Meeting.objects.get(pk=meeting_pk)

        self.assertFalse(meeting.is_accepted)

        client.force_authenticate(user=self.tutor)
        response = client.post(reverse('meeting-accept', kwargs={'pk': meeting_pk}), format='json')
        self.assertEqual(response.status_code, 200)
        meeting.refresh_from_db()
        self.assertTrue(meeting.is_accepted)

        response = client.post(reverse('meeting-cancel', kwargs={'pk': meeting_pk}), format='json')
        self.assertEqual(response.status_code, 200)
        meeting.refresh_from_db()
        self.assertTrue(meeting.is_cancelled)

        response = client.delete(reverse('meeting-cancel', kwargs={'pk': meeting_pk}), format='json')
        self.assertEqual(response.status_code, 200)
        meeting.refresh_from_db()
        self.assertFalse(meeting.is_cancelled)

    def test_review(self):
        data = {
            'rating': '3',
            'review': 'This was a great session!',
        }
        client = APIClient()
        client.force_authenticate(user=self.student)
        response = client.post(reverse('meeting-review', kwargs={'pk': self.future_meeting.pk}), data=data, format='json')
        self.assertEqual(response.status_code, 400)

        response = client.post(reverse('meeting-review', kwargs={'pk': self.past_meeting.pk}), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        meeting = Meeting.objects.get(pk=self.past_meeting.pk)
        review = meeting.review
        self.assertEqual(review.rating, 3)
        self.assertEqual(review.review, 'This was a great session!')
