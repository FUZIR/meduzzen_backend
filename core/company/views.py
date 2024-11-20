from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.utils.translation import gettext_lazy as _

from core.user.models import CustomUser
from core.user.serializers import UserListSerializer
from .models import Company
from .permissions import OwnCompanyPermission
from .serializers import CompanyListSerializer, CompanySerializer, CreateCompanySerializer


# Create your views here.
class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyListSerializer
        elif self.action == "create":
            return CreateCompanySerializer
        else:
            return CompanySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), OwnCompanyPermission()]
        else:
            return [IsAuthenticated()]

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = CreateCompanySerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

    def list(self, request: Request, **kwargs) -> Response:
        queryset = self.get_queryset()
        serialize = CompanyListSerializer(queryset, many=True)
        return Response(serialize.data, status=HTTP_200_OK)

    def retrieve(self, request: Request, pk=None, **kwargs) -> Response:
        queryset = self.get_queryset()
        company = get_object_or_404(queryset, pk=pk)
        serialize = CompanySerializer(company)
        return Response(serialize.data, status=HTTP_200_OK)

    def destroy(self, request: Request, pk=None) -> Response:
        queryset = self.get_queryset()
        company = get_object_or_404(queryset, pk=pk)
        company.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def update(self, request: Request, pk=None, **kwargs) -> Response:
        instance = self.get_object()
        serializer = CompanySerializer(instance=instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(status=HTTP_200_OK)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = CompanySerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(status=HTTP_200_OK)

class RemoveUser(APIView):
    permission_classes = [IsAuthenticated, OwnCompanyPermission]

    def post(self, request, *args, **kwargs):
        owner = request.user
        user_id = request.data.get("user")
        company_id = request.data.get("company")

        company = get_object_or_404(Company, id=company_id, owner=owner)
        user = get_object_or_404(CustomUser, id=user_id)

        if user.company != company:
            return Response({"detail": _("User is not a member of this company")}, status=HTTP_400_BAD_REQUEST)
        user.company = None
        user.save()
        return Response({"detail": _("User removed successfully")}, status=HTTP_200_OK)


class GetCompanyMembers(ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, OwnCompanyPermission]
    pagination_class = None

    def get_queryset(self):
        company_id = self.request.query_params.get("company_id")
        if not company_id:
            raise ValueError("Company ID is required")
        company = get_object_or_404(Company, id=company_id)
        self.check_object_permissions(self.request, company)
        return company.members.all()

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=HTTP_400_BAD_REQUEST)