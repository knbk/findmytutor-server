from django.utils import timezone
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsStudent

from .models import Meeting, Review
from .serializers import MeetingSerializer, ReviewSerializer


class MeetingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingSerializer

    def get_queryset(self):
        qs = self.request.user.profile.meetings.all()
        if 'past' in self.request.query_params:
            qs = qs.filter(end__lt=timezone.now()).reverse()
        elif 'future' in self.request.query_params:
            qs = qs.filter(end__gte=timezone.now())
            qs = qs.exclude(**{
                '%s_accepted_at' % self.request.user.type: None,
                '%s_cancelled_at' % self.request.user.type: None,
            })
            qs = qs.filter(tutor_cancelled_at=None, student_cancelled_at=None)
        elif 'requests' in self.request.query_params:
            qs = qs.filter(end__gte=timezone.now())
            qs = qs.filter(**{
                '%s_accepted_at' % self.request.user.type: None,
                '%s_cancelled_at' % self.request.user.type: None,
            })
        return qs

    def perform_create(self, serializer):
        data = {}
        if self.request.user.type == User.STUDENT:
            if not self.request.user.profile.tutors.filter(pk=serializer.validated_data['tutor'].pk).exists():
                self.permission_denied(self.request, 'Tutor not in My Tutors')
            data['student'] = self.request.user.student
            data['student_accepted_at'] = timezone.now()
        else:
            if not self.request.user.profile.students.filter(pk=serializer.validated_data['student'].pk).exists():
                self.permission_denied(self.request, 'Student not in My Students')
            data['tutor'] = self.request.user.tutor
            data['tutor_accepted_at'] = timezone.now()
        serializer.save(**data)

    def perform_destroy(self, instance):
        if self.request.user.type == User.STUDENT:
            instance.student_cancelled_at = timezone.now()
        else:
            instance.tutor_cancelled_at = timezone.now()
        instance.save()

    @detail_route(['post'])
    def accept(self, request, pk):
        obj = self.get_object()
        if self.request.user.type == User.STUDENT:
            obj.student_accepted_at = timezone.now()
        if self.request.user.type == User.TUTOR:
            obj.tutor_accepted_at = timezone.now()
        obj.save()
        return Response({'status': 'meeting accepted'})

    @detail_route(['post', 'delete'])
    def cancel(self, request, pk):
        obj = self.get_object()
        if self.request.user.type == User.STUDENT:
            obj.student_cancelled_at = timezone.now() if request.method == 'POST' else None
        if self.request.user.type == User.TUTOR:
            obj.tutor_cancelled_at = timezone.now() if request.method == 'POST' else None
        obj.save()
        return Response({'status': 'meeting cancelled' if request.method == 'POST' else 'meeting reopened'})

    @detail_route(['post', 'put', 'delete'], permission_classes=[IsStudent], serializer_class=ReviewSerializer)
    def review(self, request, pk):
        meeting = self.get_object()
        if meeting.end >= timezone.now():
            raise ValidationError('cannot review meetings in the future')
        if request.method == 'POST' or request.method == 'PUT':
            review = getattr(meeting, 'review', None)
            serializer = ReviewSerializer(instance=review, data=request.data)
            if serializer.is_valid():
                serializer.save(meeting=meeting)
                return Response(serializer.data, status=201 if request.method == 'POST' else 200)
            return Response(serializer.errors, status=400)
        if request.method == 'DELETE':
            review = getattr(meeting, 'review', None)
            if review:
                review.delete()
                return Response({'status': 'review deleted'})
            return Response({'status': 'no review to delete'}, status=400)
        self.http_method_not_allowed(request)
