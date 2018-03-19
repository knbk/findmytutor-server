from rest_framework import routers

from .views import StudentViewSet, UserViewSet


router = routers.SimpleRouter()
router.register(r'students', StudentViewSet)
router.register(r'users', UserViewSet)
urlpatterns = router.urls
