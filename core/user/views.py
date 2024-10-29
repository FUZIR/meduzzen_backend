from functools import partial
from logging import raiseExceptions

from django.contrib.admin.templatetags.admin_list import pagination
from rest_framework import viewsets, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND

from .models import CustomUser as User
from .serializers import UserSerializer
from .serializers import UserListSerializer


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        return UserListSerializer

    def list(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, **kwargs):
        user_id = kwargs.get("pk")
        try:
            queryset = User.objects.get(id=user_id)
            serializer = UserSerializer(queryset)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"id": user.id}, status=HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.delete()
            return Response(status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        user = request.data
        instance = self.get_object()
        serializer = UserSerializer(instance=instance,
                                           data=user,
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.data, status=status.HTTP_400_BAD_REQUEST)


