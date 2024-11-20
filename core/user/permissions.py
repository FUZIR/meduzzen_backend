from rest_framework import permissions

from core.request.models import RequestModel
from core.invitation.models import InvitationModel
from .models import CustomUser


class OwnProfilePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, CustomUser):
            return request.user.is_authenticated and obj.id == request.user.id
        elif isinstance(obj, RequestModel):
            return request.user.is_authenticated and obj.user == request.user
        elif isinstance(obj, InvitationModel):
            return request.user.is_authenticated and obj.user == request.user
        return False

    def has_permission(self, request, view):
        if hasattr(view, "action"):
            if view.action == "list":
                return request.user.is_authenticated
            elif view.action in ["create", "retrieve"]:
                user_id = request.query_params.get("user") or request.data.get("user")
                return (
                        request.user.is_authenticated
                        and user_id
                        and request.user.id == int(user_id)
                )
        return request.user.is_authenticated
