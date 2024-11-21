from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .request import RequestViewSet
from .views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"requests", RequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
