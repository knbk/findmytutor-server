from django.db import models
from django.utils import timezone


class MessageThread(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.SET_NULL, null=True,
                                related_name='message_threads')
    tutor = models.ForeignKey('accounts.Tutor', on_delete=models.SET_NULL, null=True,
                              related_name='message_threads')


class Message(models.Model):
    STUDENT = 'student'
    TUTOR = 'tutor'
    SENT_BY_CHOICES = (
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
    )
    thread = models.ForeignKey('messaging.MessageThread', on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    sent_by = models.CharField(choices=SENT_BY_CHOICES, max_length=20)
