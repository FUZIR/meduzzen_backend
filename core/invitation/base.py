from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.company.models import Company
from core.invitation.models import Status


class BaseRetrieveUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def update_status(self, instance, status: Status) -> None:
        instance.status = status
        instance.save()

    def update_user_company(self, user, instance, type: str) -> Response:
        if user:
            user.company = instance.company
            user.save()
            return Response({"detail": f"{type} accepted"}, status=status.HTTP_200_OK)

    def _check_owner_permission(self, request, instance) -> None | Response:
        if instance.company.owner != request.user:
            return Response({"detail": "You are not owner"}, status=status.HTTP_400_BAD_REQUEST)
        return None

    def handle_update(self, request, instance, status) -> None | Response:
        if not instance:
            return Response({"detail": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
        permission_response = self._check_owner_permission(request, instance)
        if permission_response:
            return permission_response
        self.update_status(instance, status)


class CompanyBaseListView(ListAPIView):
    def get_company(self):
        company_id = self.request.query_params.get("company")
        if not company_id:
            raise NotFound({"detail": "Company ID is required"})
        owner = self.request.user.id
        try:
            company = Company.objects.get(owner=owner, id=company_id)
        except Company.DoesNotExist:
            raise NotFound({"detail": "Company not found"})
        return company