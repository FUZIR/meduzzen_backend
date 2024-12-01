from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.role.permissions import IsAdminOrOwnerPermission
from .models import QuizModel
from .serializers import QuizSerializer, GetQuizSerializer


# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    queryset = QuizModel.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return GetQuizSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return QuizSerializer

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
            return QuizModel.objects.filter(company=company_id)
        return super().get_queryset()
