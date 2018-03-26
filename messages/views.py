from rest_framework import viewsets, permissions, mixins

from accounts.models import User
from .models import Message, MessageThread
from .serializers import MessageSerializer, MessageThreadSerializer


class MessageThreadViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    model = MessageThread
    serializer_class = MessageThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.type == User.STUDENT:
            return MessageThread.objects.get(student=self.request.user.student, tutor_id=self.kwargs['pk'])
        else:
            return MessageThread.objects.get(tutor=self.request.user.tutor, student_id=self.kwargs['pk'])

    def get_queryset(self):
        if self.request.user.type == User.STUDENT:
            return MessageThread.objects.filter(student=self.request.user.student)
        else:
            return MessageThread.objects.filter(tutor=self.request.user.tutor)

    def perform_update(self, serializer):
        thread = serializer.instance
        message = thread.messages.create(
            sent_by=self.request.user.type,
            content=serializer.validated_data['content'],
        )
