from django.db.models import QuerySet
from rest_framework import serializers

from core.invitation.serializers import InvitationUpdateSerializer
from .models import CustomUser as User


class UserSerializer(serializers.ModelSerializer):
    invitations = InvitationUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "description",
            "company",
            "invitations",
            "country",
            "visible",
            "image_path",
            "created_at",
            "updated_at",
        ]
        depth = 1
        extra_kwargs = {
            "password": {"write_only": True},
            "is_active": {"required": False},
            "company": {"read_only": True},
            "country": {"read_only": True},
            "id": {"read_only": True},
        }

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user



class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "company",
                  "created_at",
                  "image_path"]
        extra_kwargs = {field: {"read_only": True} for field in fields}

    def to_representation(self, instance):
        if isinstance(instance, QuerySet):
            instance = instance.order_by("created_at")
        return super().to_representation(instance)
