from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

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
