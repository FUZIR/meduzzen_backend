from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.role.permissions import IsAdminOrOwnerPermission
from .models import QuizModel
from .serializers import QuizSerializer


# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    queryset = QuizModel.objects.prefetch_related("questions__answers").all()

    def get_serializer_class(self):
        if self.action in ["list", "create", "update", "partial_update"]:
            return QuizSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminOrOwnerPermission()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == "list":
            company_id = self.request.query_params.get("company")
            if not company_id:
                return QuizModel.objects.none()
            return QuizModel.objects.filter(company=company_id).prefetch_related("questions__answers")
        return super().get_queryset()
