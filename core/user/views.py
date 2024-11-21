import djoser.serializers
from django.utils.translation import gettext as _
from rest_framework.decorators import permission_classes, action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from djoser.views import UserViewSet as DjoserViewSet

from core.invitation.models import InvitationModel
from core.invitation.serializers import InvitationUpdateSerializer
from .models import CustomUser as User
from .permissions import OwnProfilePermission
from .serializers import UserSerializer
from .serializers import UserListSerializer


# Create your views here.
class UserViewSet(DjoserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        if self.action in ["create", "login", "register"]:
            return [AllowAny()]
        elif self.action in ["update", "partial_update"]:
            return [OwnProfilePermission()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        users = User.objects.filter(visible=True)
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def get_serializer_class(self):
        if self.action in ["create", "set_password", "update", "partial_update", "retrieve"]:
            return UserSerializer
        elif self.action == "reset_password":
            return djoser.serializers.SendEmailResetSerializer
        elif self.action == "reset_password_confirm":
            return djoser.serializers.PasswordResetConfirmSerializer
        return UserListSerializer

    @permission_classes([IsAdminUser, OwnProfilePermission])
    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.delete()
            return Response(status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": _("User not found")}, status=HTTP_404_NOT_FOUND)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated, OwnProfilePermission],
            url_path="invitations")
    def get_invitations(self, request, *args, **kwargs):
        user = request.user
        user_invitations = InvitationModel.objects.filter(user=user.id)
        if not user_invitations.exists():
            return Response({"detail": "Invitation not found"}, status=HTTP_404_NOT_FOUND)
        serializer = InvitationUpdateSerializer(user_invitations, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated, OwnProfilePermission], url_path="leave")
    def leave_company(self, request, *args, **kwargs):
        user = request.user
        if not user.company:
            return Response({"detail": _("You are not a member of any company")}, status=HTTP_400_BAD_REQUEST)

        user.company = None
        user.save()
        return Response({"detail": _("You successfully leave company")}, status=HTTP_200_OK)
