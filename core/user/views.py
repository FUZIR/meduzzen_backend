import djoser.serializers
from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from djoser.views import UserViewSet as DjoserViewSet

from .models import CustomUser as User
from .serializers import UserSerializer
from .serializers import UserListSerializer


# Create your views here.
class UserViewSet(DjoserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ['create', 'set_password']:
            return UserSerializer
        elif self.action == 'reset_password':
            return djoser.serializers.SendEmailResetSerializer
        elif self.action == 'reset_password_confirm':
            return djoser.serializers.PasswordResetConfirmSerializer
        return UserListSerializer

    @permission_classes([IsAdminUser])
    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.delete()
            return Response(status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=HTTP_404_NOT_FOUND)
