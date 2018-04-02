from django.db import transaction
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route, api_view, permission_classes, renderer_classes, list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from social_django.utils import psa
from social_core.actions import do_complete

from messages.models import MessageThread
from .models import Location, Student, Tutor, User
from .permissions import IsOwnerOrReadOnly, IsParentOwnerOrReadOnly, IsStudentOrTutor
from .serializers import (LocationSerializer, StudentSerializer,
                          TutorSerializer, UserSerializer)
from .filters import TutorFilterSet


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(["GET"])
    @permission_classes([IsAuthenticated])
    def profile(self, request):
        if not request.user.type:
            return Response({}, status=404)
        serializer_class = StudentSerializer if request.user.type == User.STUDENT else TutorSerializer
        serializer = serializer_class(request.user.profile, context={'request': request})
        data = serializer.data
        data['type'] = request.user.type
        return Response(data)


class ProfileMixin:
    permission_classes = [IsOwnerOrReadOnly]

    @transaction.atomic()
    def perform_create(self, serializer):
        if self.request.user.type:
            raise ValidationError('Profile already exists.')
        serializer.save(user=self.request.user)

    @transaction.atomic()
    def perform_destroy(self, instance):
        instance.locations.all().delete()
        instance.delete()


class StudentViewSet(ProfileMixin, ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsOwnerOrReadOnly]


class TutorViewSet(ProfileMixin, ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @list_route(['get'])
    def search(self, request):
        qs = Tutor.objects.filter(available=True).annotate(rating=Avg('meetings__review__rating'))
        f = TutorFilterSet(request.query_params, queryset=qs)
        serializer = self.get_serializer(f.qs, many=True)
        return Response(serializer.data)

    @detail_route(['post', 'delete'])
    def my_tutors(self, request, pk):
        if request.user.type != User.STUDENT:
            self.permission_denied(request)
        tutor = get_object_or_404(Tutor, pk=pk)
        if request.method == "POST":
            request.user.profile.tutors.add(tutor)
            MessageThread.objects.get_or_create(student=request.user.profile, tutor=tutor)
            return Response({'status': 'tutor added to my tutors'})
        if request.method == "DELETE":
            request.user.profile.tutors.remove(tutor)
            return Response({'status': 'tutor removed from my tutors'})
        self.http_method_not_allowed(request)


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

    @transaction.atomic()
    def perform_create(self, serializer):
        parent = self.get_parent_object()
        obj = serializer.save()
        parent.locations.add(obj)


@never_cache
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
@psa('social:complete')
def obtain_auth_token(request, backend):
    response = do_complete(request.backend, _do_login, request.user, redirect_name='next', request=request)
    if response.status_code != 302:
        return response
    return Response({'key': request.user.auth_token.key})


def _do_login(backend, user, social_user):
    token, created = Token.objects.get_or_create(user=user)
    backend.strategy.request.user = user
