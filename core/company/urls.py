from django.urls import include

from rest_framework.routers import DefaultRouter
from django.urls import path

from core.company.invitation import InvitationViewSet
from core.user.request import RequestList
from .invitation import InvitationAccept, InvitationReject, InvitationRevoke
from .views import CompanyViewSet, RemoveUser, GetCompanyMembers

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"invitations", InvitationViewSet, basename="invitation")

urlpatterns = [
    path("", include(router.urls)),
    path(r"company-invitations/accept/", InvitationAccept.as_view()),
    path(r"company-invitations/reject/", InvitationReject.as_view()),
    path(r"company-invitations/revoke/", InvitationRevoke.as_view()),
    path(r"company-requests/list/", RequestList.as_view()),
    path(r"company/remove-user/", RemoveUser.as_view()),
    path(r"company/members/", GetCompanyMembers.as_view())
]
