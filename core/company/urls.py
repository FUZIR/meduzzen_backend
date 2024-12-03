from django.urls import include

from rest_framework.routers import DefaultRouter
from django.urls import path

from core.company.views.invitation import InvitationViewSet
from core.company.views.views import CompanyViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename='company')
router.register(r"invitations", InvitationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
