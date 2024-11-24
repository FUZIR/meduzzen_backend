from rest_framework import permissions
from rest_framework.exceptions import NotFound

from core.company.models import Company
from core.invitation.models import InvitationModel
from core.request.models import RequestModel


class OwnCompanyPermission(permissions.BasePermission):
    def __check_is_owner(self, request, company_id):
        return (
                request.user.is_authenticated
                and company_id
                and Company.objects.filter(id=company_id, owner=request.user).exists()
        )
    def __check_object_company_permission(self, obj_id, model, request, view):
        if obj_id:
            try:
                obj = model.objects.filter(id=obj_id).first()
                if not obj:
                    raise NotFound
                return self.has_object_permission(request, view, obj.company)
            except model.DoesNotExist:
                return False
        return False
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Company):
            return request.user.is_authenticated and obj.owner == request.user
        elif isinstance(obj, InvitationModel):
            return request.user.is_authenticated and obj.company.owner == request.user
        elif isinstance(obj, RequestModel):
            return request.user.is_authenticated and obj.company.owner == request.user
        return False

    def has_permission(self, request, view):
        if hasattr(view, "action"):
            if view.action in ["create", "retrieve", "list", "get_members"]:
                company_id = request.data.get("company") or request.query_params.get("company")
                return self.__check_is_owner(request, company_id)

            elif view.action in ["invitation_revoke"]:
                obj_id = request.data.get("id")
                return self.__check_object_company_permission(obj_id, InvitationModel, request, view)

            elif view.action in ["request_accept", "request_reject"]:
                obj_id = request.data.get("id")
                return self.__check_object_company_permission(obj_id, RequestModel, request, view)

            elif view.action in ["get_invitations", "get_requests"]:
                obj_id = request.query_params.get("company")
                if obj_id:
                    try:
                        obj = Company.objects.filter(id=obj_id).first()
                        if not obj:
                            raise NotFound
                        return self.has_object_permission(request, view, obj)
                    except Company.DoesNotExist:
                        return False
                return False
            elif view.action in ["destroy", "partial_update", "update"]:
                company_id = view.kwargs.get("pk")
                if company_id:
                    return self.__check_is_owner(request, company_id)
                return False
        return True
