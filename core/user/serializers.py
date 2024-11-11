from django.db.models import QuerySet
from rest_framework import serializers
from .models import CustomUser as User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "company",
            "image_path",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "is_active": {"required": False},
        }

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            company=validated_data["company"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "company", "created_at", "image_path"]
        extra_kwargs = {field: {"read_only": True} for field in fields}

    def to_representation(self, instance):
        if isinstance(instance, QuerySet):
            instance = instance.order_by("created_at")
        return super().to_representation(instance)
