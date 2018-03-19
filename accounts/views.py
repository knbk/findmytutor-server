from rest_framework.viewsets import ModelViewSet

from .models import Student, User
from .serializers import StudentSerializer, UserSerializer


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
