from django.test import TestCase, Client

from core.company.models import Company
from core.user.models import CustomUser
from core.invitation.models import InvitationModel
from core.invitation.models import Status
from core.invitation.models import RequestModel


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = CustomUser.objects.create_user(username="Owner", email="owner@gmail.com", password="testpassword")
        self.user = CustomUser.objects.create_user(username="TestUser", email="user@gmail.com", password="testpassword")
        self.company = Company.objects.create(name="TestCompany", company_email="company@gmail.com", image_path="",
                                              owner=self.owner)

    def login_user(self, email, password):
        token_response = self.client.post("/auth/token/login/", {
            "email": email,
            "password": password
        })
        self.assertEqual(token_response.status_code, 200)
        return token_response.data.get("auth_token")


class InvitationCreationTests(BaseTestCase):
    def test_create_invitation(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        response = self.client.post("/api/invitations/create/", {
            "user": self.user.id,
            "company": self.company.id
        }, HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(response.status_code, 201)
        self.assertIn("user", response.data)
        self.assertIn("company", response.data)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["company"], self.company.id)

    def test_create_invitation_company_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        response = self.client.post("/api/invitations/create/", {
            "user": self.user.id,
        }, HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Company not found")

    def test_create_invitation_not_owner(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        response = self.client.post("/api/invitations/create/", {
            "user": self.user.id,
            "company": self.company.id
        }, HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "You are not company owner")


class InvitationAcceptanceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.accept_invitation = InvitationModel.objects.create(user=self.user, company=self.company)

    def test_accept_invitation(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/invitations/accept/", {
            "id": self.accept_invitation.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(accept_response.status_code, 200)
        self.assertIn("detail", accept_response.data)
        self.assertEqual(accept_response.data["detail"], "Invitation accepted")

        self.accept_invitation.refresh_from_db()
        self.assertEqual(self.accept_invitation.status, Status.ACCEPTED)

    def test_accept_invitation_not_found(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/invitations/accept/", {}, content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(accept_response.status_code, 404)
        self.assertIn("detail", accept_response.data)
        self.assertEqual(accept_response.data["detail"], "Invitation not found")


class InvitationRejectionTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.reject_invitation = InvitationModel.objects.create(user=self.user, company=self.company)

    def test_reject_invitation(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch("/api/invitations/reject/", {
            "id": self.reject_invitation.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(reject_response.status_code, 200)
        self.assertIn("detail", reject_response.data)
        self.assertEqual(reject_response.data["detail"], "Invitation rejected")

        self.reject_invitation.refresh_from_db()
        self.assertEqual(self.reject_invitation.status, Status.REJECTED)

    def test_reject_invitation_not_found(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch("/api/invitations/reject/", {}, content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(reject_response.status_code, 404)
        self.assertIn("detail", reject_response.data)
        self.assertEqual(reject_response.data["detail"], "Invitation not found")


class InvitationRevocationTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.revoke_invitation = InvitationModel.objects.create(user=self.user, company=self.company)

    def test_revoke_invitation(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        revoke_response = self.client.patch("/api/invitations/revoke/", {
            "id": self.revoke_invitation.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(revoke_response.status_code, 200)
        self.assertIn("detail", revoke_response.data)
        self.assertEqual(revoke_response.data["detail"], "Invitation revoked")

        self.revoke_invitation.refresh_from_db()
        self.assertEqual(self.revoke_invitation.status, Status.REVOKED)

    def test_revoke_invitation_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        revoke_response = self.client.patch("/api/invitations/revoke/", {}, content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(revoke_response.status_code, 404)
        self.assertIn("detail", revoke_response.data)
        self.assertEqual(revoke_response.data["detail"], "Invitation not found")


class RequestCreationTests(BaseTestCase):
    def test_create_request(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        create_response = self.client.post("/api/requests/create/", {
            "user": self.user.id,
            "company": self.company.id
        }, content_type="application/json",
                                           HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(create_response.status_code, 201)
        self.assertIn("user", create_response.data)
        self.assertIn("company", create_response.data)
        self.assertEqual(create_response.data["user"], self.user.id)
        self.assertEqual(create_response.data["company"], self.company.id)

    def test_create_request_company_not_found(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        create_response = self.client.post("/api/requests/create/", {
            "user": self.user.id,
            "company": 99999
        }, HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(create_response.status_code, 404)
        self.assertIn("detail", create_response.data)
        self.assertEqual(create_response.data["detail"], "Company not found")

    def test_create_request_invalid_user(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        create_response = self.client.post("/api/requests/create/", {
            "user": self.owner.id,
            "company": self.company.id
        }, HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(create_response.status_code, 400)
        self.assertIn("detail", create_response.data)
        self.assertEqual(create_response.data["detail"], "You can't send request as another user")


class RequestAcceptationTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.acceptation_request = RequestModel.objects.create(user=self.user, company=self.company)

    def test_accept_request(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/requests/accept/", {
            "id": self.acceptation_request.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(accept_response.status_code, 200)
        self.assertIn("detail", accept_response.data)
        self.assertEqual(accept_response.data["detail"], "Request accepted")

        self.acceptation_request.refresh_from_db()
        self.assertEqual(self.acceptation_request.status, Status.ACCEPTED)

    def test_accept_request_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/requests/accept/", {"id": 9999}, content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(accept_response.status_code, 404)
        self.assertIn("detail", accept_response.data)
        self.assertEqual(accept_response.data["detail"], "Request not found")


class RequestRejectionTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.rejection_request = RequestModel.objects.create(user=self.user, company=self.company)

    def test_reject_request(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch("/api/requests/reject/", {
            "id": self.rejection_request.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(reject_response.status_code, 200)
        self.assertIn("detail", reject_response.data)
        self.assertEqual(reject_response.data["detail"], "Request rejected")

        self.rejection_request.refresh_from_db()
        self.assertEqual(self.rejection_request.status, Status.REJECTED)

    def test_reject_request_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch("/api/requests/reject/", {}, content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(reject_response.status_code, 404)
        self.assertIn("detail", reject_response.data)
        self.assertEqual(reject_response.data["detail"], "Request not found")


class RequestRevocationTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.revocation_request = RequestModel.objects.create(user=self.user, company=self.company)

    def test_revoke_invitation(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        revoke_response = self.client.patch("/api/requests/revoke/", {
            "id": self.revocation_request.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(revoke_response.status_code, 200)
        self.assertIn("detail", revoke_response.data)
        self.assertEqual(revoke_response.data["detail"], "Request revoked")

        self.revocation_request.refresh_from_db()
        self.assertEqual(self.revocation_request.status, Status.REVOKED)

    def test_revoke_invitation_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        revoke_response = self.client.patch("/api/requests/revoke/", {}, content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(revoke_response.status_code, 404)
        self.assertIn("detail", revoke_response.data)
        self.assertEqual(revoke_response.data["detail"], "Request not found")


class GetInvitedUsersTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.invitation = InvitationModel.objects.create(user=self.user, company=self.company)

    def test_get_invited_users_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/company/get-invited-users/", query_params={'company': self.company.id},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data['results']), 1)
        self.assertEqual(get_response.data['results'][0]['id'], self.invitation.id)
        self.assertEqual(get_response.data['results'][0]['user'], self.invitation.user.id)
        self.assertEqual(get_response.data['results'][0]['company'], self.invitation.company.id)
        self.assertEqual(get_response.data['results'][0]['status'], Status.PENDING)

    def test_get_invited_users_company_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/company/get-invited-users/", query_params={'company': 99999},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 404)
        self.assertIn("detail", get_response.data)
        self.assertEqual(get_response.data["detail"], "Company not found")


class GetUserRequestsTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.request = RequestModel.objects.create(company=self.company, user=self.user)

    def test_get_requests_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/company/get-users-requests/",
                                       query_params={'company': self.company.id},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data['results']), 1)
        self.assertEqual(get_response.data['results'][0]['id'], self.request.id)
        self.assertEqual(get_response.data['results'][0]['user'], self.request.user.id)
        self.assertEqual(get_response.data['results'][0]['company'], self.request.company.id)
        self.assertEqual(get_response.data['results'][0]['status'], Status.PENDING)

    def test_get_requests_company_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/company/get-users-requests/", query_params={'company': 99999},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 404)
        self.assertIn("detail", get_response.data)
        self.assertEqual(get_response.data["detail"], "Company not found")


class GetCompanyMembersTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.member = CustomUser.objects.create_user(username="member", email="member@test.com",
                                                     password="testpassword")
        self.company.members.add(self.member)

    def test_get_company_members_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)
        get_response = self.client.get("/api/company/get-company-members/",
                                       HTTP_AUTHORIZATION=f"Token {token}", query_params={'company': self.company.id})
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data['results']), 1)
        members = [member['id'] for member in get_response.data['results']]
        self.assertIn(self.member.id, members)

    def test_get_requests_company_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/company/get-company-members/", query_params={'company': 99999},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 404)
        self.assertIn("detail", get_response.data)
        self.assertEqual(get_response.data["detail"], "Company not found")


class LeaveCompanyTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.member = CustomUser.objects.create_user(username="member", email="member@test.com",
                                                     password="testpassword")
        self.company.members.add(self.member)

    def test_leave_company(self):
        token = self.login_user(self.member.email, "testpassword")
        self.assertIsNotNone(token)
        self.assertTrue(self.company.members.filter(id=self.member.id).exists())

        leave_response = self.client.post("/api/company/leave/", HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(leave_response.status_code, 200)
        self.assertIn("detail", leave_response.data)
        self.assertEqual(leave_response.data["detail"], "You successfully leave company")
        self.assertFalse(self.company.members.filter(id=self.member.id).exists())


class RemoveUserTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user_to_remove = CustomUser.objects.create_user(
            username="user", email="user@test.com", password="testpassword"
        )
        self.company.members.add(self.user_to_remove)
        self.user_to_remove.company = self.company
        self.user_to_remove.save()

    def test_remove_user_successfully(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)
        self.assertTrue(self.company.members.filter(id=self.user_to_remove.id).exists())

        remove_response = self.client.post(
            "/api/company/remove_user/",
            {"user": self.user_to_remove.id, "company": self.company.id},
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertIn("detail", remove_response.data)
        self.assertEqual(remove_response.data["detail"], "User removed successfully")
        self.assertFalse(self.company.members.filter(id=self.user_to_remove.id).exists())

    def test_remove_user_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)
        remove_response = self.client.post(
            "/api/company/remove_user/",
            {"user": 99999, "company": self.company.id},
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.assertEqual(remove_response.status_code, 404)

    def test_remove_company_not_found(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)
        remove_response = self.client.post(
            "/api/company/remove_user/",
            {"user": self.user.id, "company": self.company.id},
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.assertEqual(remove_response.status_code, 404)

