from core.request.tests import BaseTestCase
from core.user.models import CustomUser
from core.request.models import RequestModel, RequestStatus


# Create your tests here.
class GetCompanyMembersTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.member = CustomUser.objects.create_user(username="member", email="member@test.com",
                                                     password="testpassword")
        self.company.members.add(self.member)
        self.other_user = CustomUser.objects.create_user(username="other", email="other@example.com",
                                                         password="testpassword")

    def test_get_company_members_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)
        get_response = self.client.get("/api/companies/members/",
                                       query_params={"company": self.company.id},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 200)
        self.assertIsInstance(get_response.data, list)
        self.assertEqual(len(get_response.data), 1)

    def test_get_company_members_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/companies/members/",
                                       query_params={"company": 99999},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 404)

    def test_get_company_members_no_access(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)
        self.company.owner = self.other_user
        self.company.save()
        get_response = self.client.get(
            "/api/companies/members/",
            {"company": self.company.id},
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(get_response.status_code, 403)
        self.assertIn("detail", get_response.data)
        self.assertEqual(get_response.data["detail"], "You do not have permission to perform this action.")

    def test_get_company_members_missing_parameter(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        get_response = self.client.get("/api/companies/members/",
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 400)
        self.assertIn("detail", get_response.data)
        self.assertEqual(get_response.data["detail"], "Company ID is required")


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
            "/api/companies/remove-user/",
            {"user": self.user_to_remove.id, "company": self.company.id},
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertIn("detail", remove_response.data)
        self.assertEqual(remove_response.data["detail"], "User removed successfully")
        self.company.refresh_from_db()
        self.assertFalse(self.company.members.filter(id=self.user_to_remove.id).exists())

    def test_remove_user_not_found(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)
        remove_response = self.client.post(
            "/api/companies/remove-user/",
            {"user": 99999, "company": self.company.id},
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.assertEqual(remove_response.status_code, 404)

    def test_remove_company_not_found(self):
        token = self.login_user(self.user.email, "testpassword")
        self.assertIsNotNone(token)
        remove_response = self.client.post(
            "/api/companies/remove-user/",
            {"user": self.user.id, "company": self.company.id},
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.assertEqual(remove_response.status_code, 404)


class GetCompanyRequests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.request = RequestModel.objects.create(company=self.company, user=self.user)
        self.assertEqual(RequestModel.objects.count(), 1)

    def test_get_requests_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)
        get_response = self.client.get("/api/companies/request-list/", query_params={'company': self.company.id},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data), 1)
        self.assertEqual(get_response.data[0]['id'], self.request.id)
        self.assertEqual(get_response.data[0]['user'], self.request.user.id)
        self.assertEqual(get_response.data[0]['company'], self.request.company.id)
        self.assertEqual(get_response.data[0]['status'], RequestStatus.PENDING)
