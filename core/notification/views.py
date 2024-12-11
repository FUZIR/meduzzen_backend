from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from core.notification.models import NotificationModel, NotificationStatus
from core.notification.serializers import NotificationSerializer
from core.user.permissions import OwnProfilePermission


# Create your views here.
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = NotificationModel.objects.all()
    serializer_class = NotificationSerializer
    def get_queryset(self):
        if self.action == "list":
            return NotificationModel.objects.filter(user=self.request.user)
        elif self.action == "mark_notification_as_read":
            return NotificationModel.objects.filter(user=self.request.user, id=self.request.data.get("id"))
        return super().get_queryset()

    @action(methods=["PATCH"], permission_classes=[OwnProfilePermission], detail=False, url_path="mark-read")
    def mark_notification_as_read(self, request, *args, **kwargs):
        notification = get_object_or_404(self.get_queryset())
        notification.status = NotificationStatus.READ
        notification.save()
        return Response({"detail": "Notification status changed successfully"},status=HTTP_200_OK)