from rest_framework import serializers

from .models import InvitationModel


class InvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationModel
        fields = [
            "company",
            "user",
        ]


class InvitationUpdateSerializer(serializers.ModelSerializer):
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