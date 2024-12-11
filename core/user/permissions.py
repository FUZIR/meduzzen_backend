from rest_framework import permissions
from rest_framework.exceptions import NotFound

from core.invitation.models import InvitationModel
from core.notification.models import NotificationModel
from core.request.models import RequestModel

from .models import CustomUser


class OwnProfilePermission(permissions.BasePermission):
    def __check_first_model_object_permission(self, model, request, view):
        try:
            obj_id = (
                    request.data.get("id")
                    or request.query_params.get("id")
                    or view.kwargs.get("pk")
            )
            obj = model.objects.filter(id=obj_id).first()
            if not obj:
                raise NotFound
            return self.has_object_permission(request, view, obj)
        except model.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, CustomUser):
            return request.user.is_authenticated and obj.id == request.user.id
        elif isinstance(obj, RequestModel) or isinstance(obj, InvitationModel) or isinstance(obj, NotificationModel):
            return request.user.is_authenticated and obj.user == request.user
        return False

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if hasattr(view, "action"):
            user_id = request.query_params.get("user") or request.data.get("user")
            if view.action == "list":
                return request.user.is_authenticated
            elif view.action in ["create", "retrieve"]:
                return (
                        request.user.is_authenticated
                        and user_id
                        and request.user.id == int(user_id)
                )
            elif view.action in ["update", "partial_update"]:
                return True
            elif view.action in ["invitation_reject", "invitation_accept", "get_invitations"]:
                return self.__check_first_model_object_permission(InvitationModel, request, view)
            elif view.action in ["request_cancel"]:
                return self.__check_first_model_object_permission(RequestModel, request, view)
            elif view.action in ["mark_notification_as_read"]:
                return self.__check_first_model_object_permission(NotificationModel, request, view)
            return False
        return request.user.is_authenticated
