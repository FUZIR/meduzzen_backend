from django.urls import path

from .views import InvitationCreateView, RequestsCreateView, InvitationAcceptView, RequestAcceptView, \
    InvitationRejectView, RequestRejectView, InvitationRevokeView, RequestRevokeView, LeaveCompany, RemoveUser, \
    GetInvitations, GetRequests, GetUsersRequests, GetInvitedUsers, GetCompanyMembers

urlpatterns = [
    path(r'invitations/create/', InvitationCreateView.as_view()),
    path(r'invitations/list/', GetInvitations.as_view()),
    path(r'invitations/accept/', InvitationAcceptView.as_view()),
    path(r'invitations/reject/', InvitationRejectView.as_view()),
    path(r'invitations/revoke/', InvitationRevokeView.as_view()),

    path(r'requests/create/', RequestsCreateView.as_view()),
    path(r'requests/list/', GetRequests.as_view()),
    path(r'requests/accept/', RequestAcceptView.as_view()),
    path(r'requests/reject/', RequestRejectView.as_view()),
    path(r'requests/revoke/', RequestRevokeView.as_view()),

    path(r'company/leave/', LeaveCompany.as_view()),
    path(r'company/remove_user/', RemoveUser.as_view()),
    path(r'company/get-users-requests/', GetUsersRequests.as_view()),
    path(r'company/get-invited-users/', GetInvitedUsers.as_view()),
    path(r'company/get-company-members/', GetCompanyMembers.as_view()),

]
