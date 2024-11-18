from rest_framework import serializers

from .models import InvitationModel, RequestModel


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

class RequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestModel
        fields = [
            "user",
            "company"
        ]


class RequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestModel
        fields = [
            "id",
            "user",
            "company",
            "status"
        ]
        extra_kwargs = {
            "id": {"read_only": True}
        }