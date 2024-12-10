from rest_framework import serializers

from core.company.serializers import CompanyListSerializer
from core.user.serializers import UserListSerializer

from .models import InvitationModel


class InvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationModel
        fields = [
            "company",
            "user",
        ]


class InvitationUpdateSerializer(serializers.ModelSerializer):
    company = CompanyListSerializer()
    user = UserListSerializer()
    class Meta:
        model = InvitationModel
        fields = [
            "id",
            "company",
            "user",
            "status"
        ]
        extra_kwargs = {
            "id": {"read_only": True}
        }