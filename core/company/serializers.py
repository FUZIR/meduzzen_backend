from django.db.models import QuerySet
from rest_framework import serializers

from core.user.serializers import UserListSerializer
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    owner = UserListSerializer(many=False, read_only=True)
    members = UserListSerializer(many=True, read_only=True)
    class Meta:
        model = Company
        fields = [
            "name",
            "description",
            "company_email",
            "image_path",
            "owner",
            "members",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner"]

class CreateCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "name",
            "description",
            "company_email",
            "image_path",
            "owner",
        ]

    def create(self, validated_data):
        company = Company(
            name=validated_data["name"],
            description=validated_data["description"],
            company_email=validated_data["company_email"],
            image_path=validated_data["image_path"],
            owner=validated_data["owner"],
        )
        company.save()
        return company


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "description",
            "company_email",
            "owner",
        ]
        extra_kwargs = {field: {"read_only": True} for field in fields}

    def to_representation(self, instance) -> super:
        if isinstance(instance, QuerySet):
            instance = instance.order_by("created_at")
        return super().to_representation(instance)
