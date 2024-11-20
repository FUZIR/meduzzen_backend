from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.company.invitation import InvitationList
from .request import RequestViewSet, RequestAccept, RequestReject, RequestCancel
from .views import UserViewSet, LeaveCompany

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"requests", RequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(r"user-requests/accept/", RequestAccept.as_view()),
    path(r"user-requests/reject/", RequestReject.as_view()),
    path(r"user-requests/cancel/", RequestCancel.as_view()),
    path(r"user-invitations/list/", InvitationList.as_view()),
    path(r"users/company/leave/", LeaveCompany.as_view()),
]
