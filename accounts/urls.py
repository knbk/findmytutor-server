from django.urls import path, include
from rest_framework_nested import routers

from .views import StudentViewSet, UserViewSet, TutorViewSet, LocationViewSet


router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'tutors', TutorViewSet)
router.register(r'users', UserViewSet)

student_location_router = routers.NestedSimpleRouter(router, r'students', lookup='student')
student_location_router.register(r'locations', LocationViewSet, base_name='student-locations')

tutor_location_router = routers.NestedSimpleRouter(router, r'tutors', lookup='tutor')
tutor_location_router.register(r'locations', LocationViewSet, base_name='tutor-locations')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(student_location_router.urls)),
]
