from django.db.models import QuerySet
from django.template.context_processors import request
from rest_framework import serializers
from .models import CustomUser as User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password", "image_path", "created_at",
                  "updated_at"]
        extra_kwargs = {
            "is_active": {
                "required": False
            },
        }



class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "created_at"]
        extra_kwargs = {field: {"read_only": True} for field in fields}

    def to_representation(self, instance):
        if isinstance(instance, QuerySet):
            instance = instance.order_by("created_at")
        return super().to_representation(instance)
