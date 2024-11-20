from rest_framework import permissions

from core.company.models import Company
from core.invitation.models import InvitationModel
from core.request.models import RequestModel


class OwnCompanyPermission(permissions.BasePermission):
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
            if view.action in ["create", "retrieve"]:
                company_id = request.data.get("company")
                return (
                        request.user.is_authenticated
                        and company_id
                        and Company.objects.filter(id=company_id, owner=request.user).exists()
                )
            elif view.action == "list":
                company_id = request.query_params.get("company")
                return (
                        request.user.is_authenticated
                        and company_id
                        and Company.objects.filter(id=company_id, owner=request.user).exists()
                )
        return True
