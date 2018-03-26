import datetime
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from accounts.models import User, Tutor, Student
from .models import MessageThread, Message


class MessagesTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user('student', 'student@example.com', type=User.STUDENT)
        student = Student.objects.create(
            user=cls.student, date_of_birth=datetime.date(1999, 12, 31), gender='Male',
        )
        cls.tutor = User.objects.create_user('tutor', 'tutor@example.com', type=User.TUTOR)
        tutor = Tutor.objects.create(
            user=cls.tutor, date_of_birth=datetime.date(1999, 12, 31), gender='Female',
            hourly_rate='35.00', available=True,
        )
        student.tutors.add(tutor)
        cls.thread = MessageThread.objects.create(student=student, tutor=tutor)

    def test_send_message(self):
        data = {
            'content': "Hey there, let's plan a first meeting."
        }
        client = APIClient()
        client.force_authenticate(self.student)
        response = client.put(reverse('messagethread-detail', kwargs={'pk': self.tutor.profile.pk}), data=data, format='json')
        self.assertEqual(response.status_code, 200)
        thread = MessageThread.objects.get(student=self.student.profile, tutor=self.tutor.profile)
        self.assertEqual(len(thread.messages.all()), 1)
        message = thread.messages.first()
        self.assertEqual(message.thread_id, thread.pk)
        self.assertEqual(message.content, data['content'])
        self.assertIsNotNone(message.sent_at)
        self.assertEqual(message.sent_by, User.STUDENT)

    def test_get_messages(self):
        self.thread.messages.create(
            sent_by='student',
            content="Hey, let's plan a first meeting.",
        )
        self.thread.messages.create(
            sent_by='tutor',
            content="Sure, when are you available?",
        )
        self.thread.messages.create(
            sent_by='student',
            content="How about next Wednesday?",
        )
        client = APIClient()
        client.force_authenticate(self.student)
        response = client.get(reverse('messagethread-detail', kwargs={'pk': self.tutor.profile.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        messages = data['messages']
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]['content'], "Hey, let's plan a first meeting.")
        self.assertEqual(messages[1]['content'], "Sure, when are you available?")
        self.assertEqual(messages[2]['content'], "How about next Wednesday?")
        client.force_authenticate(self.tutor)
        response = client.get(reverse('messagethread-detail', kwargs={'pk': self.student.profile.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        messages = data['messages']
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]['content'], "Hey, let's plan a first meeting.")
        self.assertEqual(messages[1]['content'], "Sure, when are you available?")
        self.assertEqual(messages[2]['content'], "How about next Wednesday?")

    def test_get_message_threads(self):
        client = APIClient()
        client.force_authenticate(self.student)
        response = client.get(reverse('messagethread-list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
