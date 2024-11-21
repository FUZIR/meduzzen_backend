from django.urls import include

from rest_framework.routers import DefaultRouter
from django.urls import path

from core.company.invitation import InvitationViewSet
from .views import CompanyViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"invitations", InvitationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
