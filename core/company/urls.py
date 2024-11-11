from django.urls import include

from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CompanyViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")

urlpatterns = [
    path("", include(router.urls))
]
