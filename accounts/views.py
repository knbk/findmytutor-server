from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from .models import Location, Student, Tutor, User
from .permissions import IsOwnerOrReadOnly, IsParentOwnerOrReadOnly
from .serializers import (LocationSerializer, StudentSerializer,
                          TutorSerializer, UserSerializer)


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.type:
            raise ValidationError('Profile already exists.')
        serializer.save(user=self.request.user)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TutorViewSet(ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.type:
            raise ValidationError('Profile already exists.')
        serializer.save(user=self.request.user)


class LocationViewSet(ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = [IsParentOwnerOrReadOnly]

    def get_parent_object(self):
        if 'student_pk' in self.kwargs:
            obj = get_object_or_404(Student, pk=self.kwargs['student_pk'])
        else:
            obj = get_object_or_404(Tutor, pk=self.kwargs['tutor_pk'])
        return obj

    def get_queryset(self):
        obj = self.get_parent_object()
        return obj.locations.all()
