from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.viewsets import ModelViewSet
from django.utils.translation import gettext_lazy as _

from core.company.models import Company
from core.company.permissions import OwnCompanyPermission
from core.request.serializers import RequestCreateSerializer, RequestUpdateSerializer
from core.request.models import RequestModel, RequestStatus
from core.user.permissions import OwnProfilePermission
from core.role.models import RoleModel


class RequestViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, OwnProfilePermission]
    queryset = RequestModel.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "create":
            return RequestCreateSerializer
        if self.action in ["list", "retrieve", "get_requests"]:
            return RequestUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == "list":
            return RequestModel.objects.filter(user=self.request.user.id)
        if self.action in ["request_accept", "request_reject", "request_cancel"]:
            return RequestModel.objects.filter(status=RequestStatus.PENDING, id=self.request.data.get("id"))
        if self.action == "get_requests":
            company = Company.objects.get(id=self.request.query_params.get("company"))
            return RequestModel.objects.filter(company=company)
        return RequestModel.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": _("There is no requests")}, status=HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, url_path="request-accept",
            permission_classes=[IsAuthenticated, OwnCompanyPermission])
    def request_accept(self, request, *args, **kwargs):
        with transaction.atomic():
            user_request = get_object_or_404(self.get_queryset())
            user = user_request.user
            company = user_request.company
            user_request.status = RequestStatus.ACCEPTED
            user_request.save()

            user.company = company
            user.save()
            RoleModel.objects.create(user=user, company=company)
        return Response({"detail": _("Request accepted successfully")}, status=HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, url_path="request-reject",
            permission_classes=[IsAuthenticated, OwnCompanyPermission])
    def request_reject(self, request, *args, **kwargs):
        user_request = get_object_or_404(self.get_queryset())
        user_request.status = RequestStatus.REJECTED
        user_request.save()
        return Response({"detail": _("Request rejected successfully")}, status=HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, url_path="request-cancel", permission_classes=[IsAuthenticated,
                                                                                            OwnProfilePermission])
    def request_cancel(self, request, *args, **kwargs):
        user_request = get_object_or_404(self.get_queryset())
        user_request.status = RequestStatus.CANCELED
        user_request.save()
        return Response({"detail": _("Request canceled successfully")}, status=HTTP_200_OK)

    @action(methods=["GET"], url_path="request-list", detail=False,
            permission_classes=[IsAuthenticated, OwnCompanyPermission])
    def get_requests(self, request, *args, **kwargs):
        requests = self.get_queryset()
        if not requests.exists():
            return Response({"detail": _("There is no requests")}, status=HTTP_404_NOT_FOUND)
        serializer = RequestUpdateSerializer(requests, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
