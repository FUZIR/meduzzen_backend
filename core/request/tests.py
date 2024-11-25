from django.test import Client, TestCase

from core.company.models import Company
from core.request.models import RequestModel, RequestStatus
from core.user.models import CustomUser


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


# Create your tests here.
class RequestCreationTests(BaseTestCase):
    def test_create_request(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        create_response = self.client.post("/api/requests/", {
            "user": self.user.id,
            "company": self.company.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(create_response.status_code, 201)
        self.assertIn("user", create_response.data)
        self.assertIn("company", create_response.data)
        self.assertEqual(create_response.data["user"], self.user.id)
        self.assertEqual(create_response.data["company"], self.company.id)

    def test_create_request_invalid_user(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        create_response = self.client.post("/api/requests/", {
            "user": self.owner.id,
            "company": self.company.id
        }, HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(create_response.status_code, 403)
        self.assertIn("detail", create_response.data)
        self.assertEqual(create_response.data["detail"], "You do not have permission to perform this action.")


class RequestAcceptationTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.acceptation_request = RequestModel.objects.create(user=self.user, company=self.company)

    def test_accept_request(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/requests/request-accept/", {
            "id": self.acceptation_request.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(accept_response.status_code, 200)
        self.assertIn("detail", accept_response.data)
        self.assertEqual(accept_response.data["detail"], "Request accepted successfully")

        self.acceptation_request.refresh_from_db()
        self.assertEqual(self.acceptation_request.status, RequestStatus.ACCEPTED)

    def test_accept_request_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/requests/request-accept/", {"id": 9999},
                                            content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(accept_response.status_code, 404)

    def test_accept_permission(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        accept_response = self.client.patch("/api/requests/request-accept/", {"id": self.acceptation_request.id},
                                            content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(accept_response.status_code, 403)
        self.assertIn("detail", accept_response.data)
        self.assertEqual(str(accept_response.data["detail"]), "You do not have permission to perform this action.")


class RequestRejectionTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.rejection_request = RequestModel.objects.create(user=self.user, company=self.company)

    def test_reject_request(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch(
            "/api/requests/request-reject/",
            {"id": self.rejection_request.id},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
            follow=True,
        )
        self.assertEqual(reject_response.status_code, 200)
        self.assertIn("detail", reject_response.data)
        self.assertEqual(reject_response.data["detail"], "Request rejected successfully")

        self.rejection_request.refresh_from_db()
        self.assertEqual(self.rejection_request.status, RequestStatus.REJECTED)

    def test_reject_request_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch("/api/requests/request-reject/", {"id": 10000},
                                            content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(reject_response.status_code, 404)

    def test_reject_permission(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        reject_response = self.client.patch("/api/requests/request-reject/", {"id": self.rejection_request.id},
                                            content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(reject_response.status_code, 403)
        self.assertIn("detail", reject_response.data)
        self.assertEqual(str(reject_response.data["detail"]), "You do not have permission to perform this action.")


class RequestCancelationTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.cancel_request = RequestModel.objects.create(user=self.user, company=self.company)

    def test_cancel_request(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        revoke_response = self.client.patch("/api/requests/request-cancel/", {
            "id": self.cancel_request.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.assertEqual(revoke_response.status_code, 200)
        self.assertIn("detail", revoke_response.data)
        self.assertEqual(revoke_response.data["detail"], "Request canceled successfully")

        self.cancel_request.refresh_from_db()
        self.assertEqual(self.cancel_request.status, RequestStatus.CANCELED)

    def test_cancel_request_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        revoke_response = self.client.patch("/api/requests/request-cancel/", {}, content_type="application/json",
                                            HTTP_AUTHORIZATION=f"Token {token}", follow=True)
        self.assertEqual(revoke_response.status_code, 404)


class GetUserRequestsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.request = RequestModel.objects.create(company=self.company, user=self.user)

    def test_get_user_requests_success(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/requests/", HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data), 1)
        self.assertEqual(get_response.data[0]['id'], self.request.id)
        self.assertEqual(get_response.data[0]['user'], self.request.user.id)
        self.assertEqual(get_response.data[0]['company'], self.request.company.id)
        self.assertEqual(get_response.data[0]['status'], RequestStatus.PENDING)

    def test_get_requests_company_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/requests/", HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 404)


class GetCompanyRequestsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.request = RequestModel.objects.create(company=self.company, user=self.user)
        self.assertEqual(RequestModel.objects.count(), 1)

    def test_get_requests_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)
        get_response = self.client.get("/api/requests/request-list/", query_params={'company': self.company.id},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data), 1)
        self.assertEqual(get_response.data[0]['id'], self.request.id)
        self.assertEqual(get_response.data[0]['user'], self.request.user.id)
        self.assertEqual(get_response.data[0]['company'], self.request.company.id)
        self.assertEqual(get_response.data[0]['status'], RequestStatus.PENDING)
