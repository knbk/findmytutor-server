from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import MeetingViewSet


router = SimpleRouter()
router.register(r'meetings', MeetingViewSet, base_name='meeting')

urlpatterns = router.urls
