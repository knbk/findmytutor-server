from rest_framework.viewsets import ModelViewSet

from .models import Location, Student, Tutor, User
from .serializers import (LocationSerializer, StudentSerializer,
                          TutorSerializer, UserSerializer)


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TutorViewSet(ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
