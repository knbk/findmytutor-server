from django.db import models


class Meeting(models.Model):
    tutor = models.ForeignKey('accounts.Tutor', on_delete=models.CASCADE, related_name='meetings')
    tutor_accepted_at = models.DateTimeField(null=True, blank=True)
    tutor_cancelled_at = models.DateTimeField(null=True, blank=True)

    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='meetings')
    student_accepted_at = models.DateTimeField(null=True, blank=True)
    student_cancelled_at = models.DateTimeField(null=True, blank=True)

    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.ForeignKey('accounts.Location', on_delete=models.SET_NULL, null=True, related_name='meetings')

    @property
    def is_accepted(self):
        return self.tutor_accepted_at is not None and self.student_accepted_at is not None

    @property
    def is_cancelled(self):
        return self.tutor_cancelled_at is not None or self.student_cancelled_at is not None


class Review(models.Model):
    RATINGS = tuple((i, str(i)) for i in range(6))
    meeting = models.OneToOneField('meetings.Meeting', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATINGS)
    review = models.TextField(blank=True)
