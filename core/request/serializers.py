from rest_framework import serializers

from .models import RequestModel


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