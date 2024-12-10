from django.db.models import Q
from rest_framework import permissions

from core.company.models import Company
from core.invitation.models import InvitationModel
from core.quiz.models import QuizModel
from core.request.models import RequestModel
from core.role.models import RoleModel, UserRoles


class IsAdminOrOwnerPermission(permissions.BasePermission):
    def __check_is_admin_or_owner(self, request, company_id):
        if not company_id:
            return False
        return (request.user.is_authenticated and (
            RoleModel.objects.filter(Q(role=UserRoles.ADMIN) | Q(role=UserRoles.OWNER), user=request.user,
                                     company=company_id).exists()))

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Company):
            return self.__check_is_admin_or_owner(request, obj.id)
        elif isinstance(obj, InvitationModel) or isinstance(obj, RequestModel) or isinstance(obj, QuizModel):
            return self.__check_is_admin_or_owner(request, obj.company.id)
        return False

    def has_permission(self, request, view):
        if hasattr(view, "action"):
            if view.action in ["update", "partial_update", "destroy"]:
                quiz_id = view.kwargs.get("pk")
                quiz = QuizModel.objects.get(id=quiz_id)
                return self.__check_is_admin_or_owner(request, quiz.company.id)
            elif view.action == "create":
                company_id = request.data.get("company")
                return self.__check_is_admin_or_owner(request, company_id)
            elif view.action in ["get_admins", "get_company_results", "get_company_average_score",
                                 "company_quizzes_history", "get_company_users_with_last_test", "get_user_results_by_id"]:
                company_id = request.query_params.get("company")
                return self.__check_is_admin_or_owner(request, company_id)
            return False
        return True
