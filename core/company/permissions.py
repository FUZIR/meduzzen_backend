from django.shortcuts import get_object_or_404
from rest_framework import permissions

from core.company.models import Company
from core.invitation.models import InvitationModel
from core.request.models import RequestModel
from core.role.models import RoleModel, UserRoles
from core.quiz.models import QuizModel


class OwnCompanyPermission(permissions.BasePermission):
    def __check_is_owner(self, request, company_id):
        if not company_id:
            return False
        return (request.user.is_authenticated and RoleModel.objects.filter(user=request.user, company_id=company_id,
                                                                           role=UserRoles.OWNER).exists())

    def __check_object_company_permission(self, obj_id, model, request, view):
        if obj_id:
            obj = get_object_or_404(model, id=obj_id)
            return self.has_object_permission(request, view, obj)
        return False

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Company):
            return self.__check_is_owner(request, obj.id)
        elif isinstance(obj, InvitationModel):
            return self.__check_is_owner(request, obj.company.id)
        elif isinstance(obj, RequestModel):
            return self.__check_is_owner(request, obj.company.id)
        elif isinstance(obj, QuizModel):
            return self.__check_is_owner(request, obj.company.id if obj.company else None)
        return False

    def has_permission(self, request, view):
        if hasattr(view, "action"):
            if view.action in ["create", "retrieve", "list", "get_members", "appoint-admin", "remove-admin", "admins"]:
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
                return self.__check_object_company_permission(obj_id, Company, request, view)
            elif view.action in ["destroy", "partial_update", "update"]:
                company_id = view.kwargs.get("pk")
                if company_id:
                    return self.__check_is_owner(request, company_id)
                return False
        return True
