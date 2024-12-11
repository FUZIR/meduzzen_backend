from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.user.views.request import RequestViewSet
from core.user.views.views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"requests", RequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
