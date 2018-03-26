from django.urls import path, include
from rest_framework import routers

from .views import MessageThreadViewSet


router = routers.DefaultRouter()
router.register(r'messages/', MessageThreadViewSet, base_name='messagethread')

urlpatterns = router.urls
