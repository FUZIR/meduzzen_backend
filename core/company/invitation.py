
from rest_framework.decorators import action
from django.db import transaction
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.viewsets import ModelViewSet

from core.invitation.serializers import InvitationCreateSerializer, InvitationUpdateSerializer
from core.invitation.models import InvitationModel
from core.invitation.models import InvitationStatus
from core.user.permissions import OwnProfilePermission
from .permissions import OwnCompanyPermission


class InvitationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, OwnCompanyPermission]
    queryset = InvitationModel.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return InvitationCreateSerializer
        if self.action in ["list", "retrieve"]:
            return InvitationUpdateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        company_id = request.query_params.get("company")
        queryset = self.get_queryset().filter(company=company_id)
        self.check_object_permissions(request, queryset[0])
        if not queryset.exists():
            return Response({"detail": "There are no invitations"}, status=HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, queryset.first())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, permission_classes=[IsAuthenticated, OwnProfilePermission],
            url_path="invitation-accept")
    def invitation_accept(self, request, *args, **kwargs):
        with transaction.atomic():
            request_id = request.data.get("id")
            user_invitation = get_object_or_404(self.get_queryset(), status=InvitationStatus.PENDING, id=request_id)
            self.check_object_permissions(request, user_invitation)
            user = request.user
            company = user_invitation.company
            user_invitation.status = InvitationStatus.ACCEPTED
            user_invitation.save()

            user.company = company
            user.save()
        return Response({"detail": "Invitation accepted successfully"}, status=HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, permission_classes=[IsAuthenticated, OwnProfilePermission],
            url_path="invitation-reject")
    def invitation_reject(self, request, *args, **kwargs):
        request_id = request.data.get("id")
        user_invitation = get_object_or_404(self.get_queryset(), status=InvitationStatus.PENDING, id=request_id)
        self.check_object_permissions(request, user_invitation)
        user_invitation.status = InvitationStatus.REJECTED
        user_invitation.save()
        return Response({"detail": "Invitation rejected successfully"}, status=HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, permission_classes=[IsAuthenticated, OwnCompanyPermission],
            url_path="invitation-revoke")
    def invitation_revoke(self, request, *args, **kwargs):
        request_id = request.data.get("id")
        user_invitation = get_object_or_404(self.get_queryset(), status=InvitationStatus.PENDING, id=request_id)
        self.check_object_permissions(request, user_invitation)
        user_invitation.status = InvitationStatus.REVOKED
        user_invitation.save()
        return Response({"detail": "Invitation revoked successfully"})

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated, OwnProfilePermission], url_path="invitations")
    def get_invitations(self, request, *args, **kwargs):
        user = request.user
        user_invitations = self.get_queryset().filter(user=user.id)
        if not user_invitations.exists():
            return Response({"detail": "Invitation not found"}, status=HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user_invitations, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
