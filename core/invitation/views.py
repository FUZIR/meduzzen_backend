from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

from core.company.models import Company
from core.user.models import CustomUser
from core.user.serializers import UserListSerializer
from .models import InvitationModel, RequestModel, Status
from .serializers import InvitationCreateSerializer, RequestCreateSerializer, InvitationUpdateSerializer, \
    RequestUpdateSerializer
from .base import BaseRetrieveUpdateView, CompanyBaseListView


# Create your views here.
class InvitationCreateView(CreateAPIView):
    serializer_class = InvitationCreateSerializer
    queryset = InvitationModel.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        owner = request.user
        company_id = request.data.get('company')
        if company_id is None:
            return Response({"detail": _("Company not found")}, status=HTTP_404_NOT_FOUND)
        if not Company.objects.filter(owner=owner, id=company_id).exists():
            return Response({"detail": _("You are not company owner")}, status=HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)


class InvitationAcceptView(BaseRetrieveUpdateView):
    serializer_class = InvitationUpdateSerializer
    queryset = InvitationModel.objects.filter(status=Status.PENDING)
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        user_id = request.user.id
        user = CustomUser.objects.filter(pk=user_id).first()
        try:
            invitation = self.get_queryset().get(user=user_id, pk=request.data.get("id"))
            self.update_status(invitation, Status.ACCEPTED)
            update_user_company_response = self.update_user_company(user, invitation, "Invitation")
            if isinstance(update_user_company_response, Response):
                return update_user_company_response
        except InvitationModel.DoesNotExist:
            return Response({"detail": _("Invitation not found")}, status=HTTP_404_NOT_FOUND)


class InvitationRejectView(BaseRetrieveUpdateView):
    serializer_class = InvitationUpdateSerializer
    queryset = InvitationModel.objects.filter(status=Status.PENDING)
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        user_id = request.user.id
        try:
            invitation = self.get_queryset().get(user=user_id, pk=request.data.get("id"))
            self.update_status(invitation, status=Status.REJECTED)
            return Response({"detail": _("Invitation rejected")}, status=HTTP_200_OK)
        except InvitationModel.DoesNotExist:
            return Response({"detail": _("Invitation not found")}, status=HTTP_404_NOT_FOUND)


class InvitationRevokeView(BaseRetrieveUpdateView):
    serializer_class = InvitationUpdateSerializer
    queryset = InvitationModel.objects.filter(status=Status.PENDING)
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        invitation_id = request.data.get("id")
        try:
            invitation = self.get_queryset().get(pk=invitation_id)
            handle_update_response = self.handle_update(request, invitation, status=Status.REVOKED)
            if isinstance(handle_update_response, Response):
                return handle_update_response
            return Response({"detail": _("Invitation revoked")}, status=HTTP_200_OK)
        except InvitationModel.DoesNotExist:
            return Response({"detail": _("Invitation not found")}, status=HTTP_404_NOT_FOUND)


class GetInvitations(ListAPIView):
    serializer_class = InvitationUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        return InvitationModel.objects.filter(user=user_id)


class GetRequests(ListAPIView):
    serializer_class = RequestUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        return RequestModel.objects.filter(user=user_id)


class GetInvitedUsers(CompanyBaseListView):
    serializer_class = InvitationUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = self.get_company()
        return InvitationModel.objects.filter(company=company.id)


class GetUsersRequests(CompanyBaseListView):
    serializer_class = RequestUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = self.get_company()
        return RequestModel.objects.filter(company=company.id)


class GetCompanyMembers(CompanyBaseListView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = self.get_company()
        return company.members.all()


class RequestsCreateView(CreateAPIView):
    serializer_class = RequestCreateSerializer
    queryset = RequestModel.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company_id = request.data.get('company')
        user = request.user
        request_user_id = request.data.get('user')
        if company_id is None:
            return Response({"detail": _("Company ID is required")}, status=HTTP_400_BAD_REQUEST)
        if not Company.objects.filter(id=company_id).exists():
            return Response({"detail": _("Company not found")}, status=HTTP_404_NOT_FOUND)
        if user.id != request_user_id:
            return Response({"detail": _("You can't send request as another user")}, status=HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)


class RequestAcceptView(BaseRetrieveUpdateView):
    serializer_class = RequestUpdateSerializer
    queryset = RequestModel.objects.filter(status=Status.PENDING)
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        request_id = request.data.get("id")
        if not request_id:
            return Response({"detail": _("Request ID is required")}, status=HTTP_400_BAD_REQUEST)

        try:
            request_instance = self.get_queryset().get(id=request_id)
        except RequestModel.DoesNotExist:
            return Response({"detail": _("Request not found")}, status=HTTP_404_NOT_FOUND)

        user = request_instance.user
        try:
            handle_update_response = self.handle_update(request, request_instance, Status.ACCEPTED)
            if isinstance(handle_update_response, Response):
                return handle_update_response

            update_user_company_response = self.update_user_company(user, request_instance, "Request")
            if isinstance(update_user_company_response, Response):
                return update_user_company_response
        except Exception as e:
            return Response({"detail": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class RequestRejectView(BaseRetrieveUpdateView):
    serializer_class = RequestUpdateSerializer
    queryset = RequestModel.objects.filter(status=Status.PENDING)
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        request_id = request.data.get("id")
        try:
            request_instance = self.get_queryset().get(id=request_id)
            handle_update_response = self.handle_update(request, request_instance, Status.REJECTED)
            if isinstance(handle_update_response, Response):
                return handle_update_response
            return Response({"detail": _("Request rejected")}, status=HTTP_200_OK)
        except RequestModel.DoesNotExist:
            return Response({"detail": _("Request not found")}, status=HTTP_404_NOT_FOUND)


class RequestRevokeView(BaseRetrieveUpdateView):
    serializer_class = RequestUpdateSerializer
    queryset = RequestModel.objects.filter(status=Status.PENDING)
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        user_id = request.user.id
        request_id = request.data.get("id")
        try:
            request_instance = self.get_queryset().get(user=user_id, id=request_id)
            self.update_status(request_instance, Status.REVOKED)
            return Response({"detail": _("Request revoked")}, status=HTTP_200_OK)
        except RequestModel.DoesNotExist:
            return Response({"detail": _("Request not found")}, status=HTTP_404_NOT_FOUND)


class LeaveCompany(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.company:
            return Response({"detail": _("You are not a member of any company")}, status=HTTP_400_BAD_REQUEST)

        user.company = None
        user.save()
        return Response({"detail": _("You successfully leave company")}, status=HTTP_200_OK)


class RemoveUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        owner = request.user
        user_id = request.data.get("user")
        company_id = request.data.get("company")

        company = get_object_or_404(Company, id=company_id, owner=owner)
        user = get_object_or_404(CustomUser,id=user_id)

        if user.company != company:
            return Response({"detail":_("User is not a member of this company")}, status=HTTP_400_BAD_REQUEST)
        user.company = None
        user.save()
        return Response({"detail": _("User removed successfully")}, status=HTTP_200_OK)
