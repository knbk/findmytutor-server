from rest_framework import routers

from .views import StudentViewSet, UserViewSet, TutorViewSet


router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'tutors', TutorViewSet)
router.register(r'users', UserViewSet)
urlpatterns = router.urls
