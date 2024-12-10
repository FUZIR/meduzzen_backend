from rest_framework import serializers

from core.notification.models import NotificationModel
from core.user.models import CustomUser


class NotificationSerializer(serializers.ModelSerializer):
    user = CustomUser()
    class Meta:
        model = NotificationModel
        fields = "__all__"