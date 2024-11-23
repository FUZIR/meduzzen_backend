from core.company.models import Company
from core.invitation.models import InvitationModel
from core.invitation.models import InvitationStatus
from core.request.tests import BaseTestCase


class InvitationCreationTests(BaseTestCase):
    def test_create_invitation(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        response = self.client.post("/api/invitations/", {
            "user": self.user.id,
            "company": self.company.id
        }, HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(response.status_code, 201)
        self.assertIn("user", response.data)
        self.assertIn("company", response.data)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["company"], self.company.id)

    def test_create_invitation_no_permission(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        response = self.client.post("/api/invitations/", {
            "user": self.user.id,
            "company": self.company.id
        }, HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")


class InvitationAcceptanceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.accept_invitation = InvitationModel.objects.create(user=self.user, company=self.company)

    def test_accept_invitation(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/invitations/invitation-accept/", {
            "id": self.accept_invitation.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(accept_response.status_code, 200)
        self.assertIn("detail", accept_response.data)
        self.assertEqual(accept_response.data["detail"], "Invitation accepted successfully")

        self.accept_invitation.refresh_from_db()
        self.assertEqual(self.accept_invitation.status, InvitationStatus.ACCEPTED)

    def test_accept_invitation_no_permission(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/invitations/invitation-accept/", {
            "id": self.accept_invitation.id
        }, content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(accept_response.status_code, 403)
        self.assertIn("detail", accept_response.data)
        self.assertEqual(accept_response.data["detail"], "You do not have permission to perform this action.")


class InvitationRejectionTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.reject_invitation = InvitationModel.objects.create(user=self.user, company=self.company)

    def test_reject_invitation(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch("/api/invitations/invitation-reject/", {
            "id": self.reject_invitation.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(reject_response.status_code, 200)
        self.assertIn("detail", reject_response.data)
        self.assertEqual(reject_response.data["detail"], "Invitation rejected successfully")

        self.reject_invitation.refresh_from_db()
        self.assertEqual(self.reject_invitation.status, InvitationStatus.REJECTED)

    def test_reject_invitation_no_permission(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch("/api/invitations/invitation-reject/", {
            "id": self.reject_invitation.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(reject_response.status_code, 403)
        self.assertIn("detail", reject_response.data)
        self.assertEqual(reject_response.data["detail"], "You do not have permission to perform this action.")


class InvitationRevocationTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.revoke_invitation = InvitationModel.objects.create(user=self.user, company=self.company)

    def test_revoke_invitation(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        revoke_response = self.client.patch("/api/invitations/invitation-revoke/", {
            "id": self.revoke_invitation.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(revoke_response.status_code, 200)
        self.assertIn("detail", revoke_response.data)
        self.assertEqual(revoke_response.data["detail"], "Invitation revoked successfully")

        self.revoke_invitation.refresh_from_db()
        self.assertEqual(self.revoke_invitation.status, InvitationStatus.REVOKED)

    def test_revoke_invitation_no_permission(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        revoke_response = self.client.patch("/api/invitations/invitation-revoke/", {
            "id": self.revoke_invitation.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(revoke_response.status_code, 403)
        self.assertIn("detail", revoke_response.data)
        self.assertEqual(revoke_response.data["detail"], "You do not have permission to perform this action.")


class GetInvitedUsersTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.second_company = Company.objects.create(name="NewCompany13", company_email="email@gmail.com",
                                                     owner=self.owner, image_path="", description="description")
        self.invitation = InvitationModel.objects.create(user=self.user, company=self.second_company)

    def test_get_invited_users_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/invitations/get-invitations/",{"company": self.second_company.id},
                                        content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}",
                                        follow=True)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data), 1)
        self.assertEqual(get_response.data[0]['id'], self.invitation.id)
        self.assertEqual(get_response.data[0]['user'], self.invitation.user.id)
        self.assertEqual(get_response.data[0]['company'], self.invitation.company.id)
        self.assertEqual(get_response.data[0]['status'], InvitationStatus.PENDING)

    def test_get_invited_users_no_permission(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)
        get_response = self.client.get("/api/invitations/get-invitations/", {"company": self.second_company.id},
                                       content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}",
                                       follow=True)
        self.assertEqual(get_response.status_code, 403)
        self.assertIn("detail", get_response.data)
        self.assertEqual(get_response.data["detail"], "You do not have permission to perform this action.")
