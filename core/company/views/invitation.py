from rest_framework.decorators import action
from django.db import transaction
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.viewsets import ModelViewSet
from django.utils.translation import gettext_lazy as _

from core.invitation.serializers import InvitationCreateSerializer, InvitationUpdateSerializer
from core.invitation.models import InvitationModel
from core.invitation.models import InvitationStatus
from core.user.permissions import OwnProfilePermission
from core.company.permissions import OwnCompanyPermission


class InvitationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, OwnCompanyPermission]
    queryset = InvitationModel.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return InvitationCreateSerializer
        if self.action in ["list", "retrieve", "get_invitations"]:
            return InvitationUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == "list":
            return InvitationModel.objects.filter(user=self.request.user)
        elif self.action in ["invitation_accept", "invitation_reject", "invitation_revoke"]:
            return InvitationModel.objects.filter(status=InvitationStatus.PENDING, id=self.request.data.get("id"))
        elif self.action == "get_invitations":
            return InvitationModel.objects.filter(company_id=self.request.query_params.get("company"))
        return super().get_queryset()

    @action(methods=["PATCH"], detail=False, permission_classes=[IsAuthenticated, OwnProfilePermission],
            url_path="invitation-accept")
    def invitation_accept(self, request, *args, **kwargs):
        with transaction.atomic():
            user_invitation = get_object_or_404(self.get_queryset())
            user = request.user
            company = user_invitation.company
            user_invitation.status = InvitationStatus.ACCEPTED
            user_invitation.save()

            user.company = company
            user.save()
        return Response({"detail": _("Invitation accepted successfully")}, status=HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, permission_classes=[IsAuthenticated, OwnProfilePermission],
            url_path="invitation-reject")
    def invitation_reject(self, request, *args, **kwargs):
        user_invitation = get_object_or_404(self.get_queryset())
        user_invitation.status = InvitationStatus.REJECTED
        user_invitation.save()
        return Response({"detail": _("Invitation rejected successfully")}, status=HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, permission_classes=[IsAuthenticated, OwnCompanyPermission],
            url_path="invitation-revoke")
    def invitation_revoke(self, request, *args, **kwargs):
        user_invitation = get_object_or_404(self.get_queryset())
        user_invitation.status = InvitationStatus.REVOKED
        user_invitation.save()
        return Response({"detail": _("Invitation revoked successfully")})

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated, OwnCompanyPermission],
            url_path="get-invitations")
    def get_invitations(self, request, *args, **kwargs):
        company_invitations = self.get_queryset()
        if not company_invitations.exists():
            return Response({"detail": _("Invitation not found")}, status=HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(company_invitations, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
