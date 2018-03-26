from django.urls import path, include
from rest_framework_nested import routers

from meetings.views import MeetingViewSet
from .views import StudentViewSet, UserViewSet, TutorViewSet, LocationViewSet


router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'tutors', TutorViewSet)
router.register(r'users', UserViewSet)
router.register(r'meetings', MeetingViewSet, base_name='meeting')

student_location_router = routers.NestedDefaultRouter(router, r'students', lookup='student')
student_location_router.register(r'locations', LocationViewSet, base_name='student-locations')

tutor_location_router = routers.NestedDefaultRouter(router, r'tutors', lookup='tutor')
tutor_location_router.register(r'locations', LocationViewSet, base_name='tutor-locations')

urlpatterns = router.urls + student_location_router.urls + tutor_location_router.urls
urlpatterns += [
    path('', include('messages.urls')),
]
