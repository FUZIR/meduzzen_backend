from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.viewsets import ModelViewSet

from core.company.permissions import OwnCompanyPermission
from core.request.serializers import RequestCreateSerializer, RequestUpdateSerializer
from core.request.models import RequestModel, RequestStatus
from .permissions import OwnProfilePermission


class RequestViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, OwnProfilePermission]
    queryset = RequestModel.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "create":
            return RequestCreateSerializer
        if self.action in ["list", "retrieve", "request-list"]:
            return RequestUpdateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        user_id = self.request.user.id
        queryset = self.get_queryset().filter(user=user_id)
        if not queryset.exists():
            return Response({"detail": "There is no requests"}, status=HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, url_path="request-accept",
            permission_classes=[IsAuthenticated, OwnCompanyPermission])
    def request_accept(self, request, *args, **kwargs):
        with transaction.atomic():
            request_id = request.data.get("id")
            user_request = get_object_or_404(self.get_queryset(), status=RequestStatus.PENDING, id=request_id)
            self.check_object_permissions(request, user_request)
            user = user_request.user
            company = user_request.company
            user_request.status = RequestStatus.ACCEPTED
            user_request.save()

            user.company = company
            user.save()
        return Response({"detail": "Request accepted successfully"}, status=HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, url_path="request-reject",
            permission_classes=[IsAuthenticated, OwnCompanyPermission])
    def request_reject(self, request, *args, **kwargs):
        request_id = request.data.get("id")
        user_request = get_object_or_404(self.get_queryset(), status=RequestStatus.PENDING, id=request_id)
        self.check_object_permissions(request, user_request)
        user_request.status = RequestStatus.REJECTED
        user_request.save()
        return Response({"detail": "Request rejected successfully"}, status=HTTP_200_OK)

    @action(methods=["PATCH"], detail=False, url_path="request-cancel")
    def request_cancel(self, request, *args, **kwargs):
        request_id = request.data.get("id")

        user_request = get_object_or_404(self.get_queryset(), status=RequestStatus.PENDING, id=request_id)
        self.check_object_permissions(request, user_request)
        user_request.status = RequestStatus.CANCELED
        user_request.save()
        return Response({"detail": "Request canceled successfully"}, status=HTTP_200_OK)

