from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route

from accounts.models import User

from .models import Meeting, Review
from .serializers import MeetingSerializer, ReviewSerializer


class MeetingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingSerializer

    def get_queryset(self):
        return self.request.user.profile.meetings.all()

    def perform_create(self, serializer):
        data = {}
        if self.request.user.type == User.STUDENT:
            data['student'] = self.request.user.student
            data['student_accepted_at'] = timezone.now()
        else:
            data['tutor'] = self.request.user.tutor
            data['tutor_accepted_at'] = timezone.now()
        serializer.save(**data)
