from core.request.tests import BaseTestCase
from core.role.models import RoleModel, UserRoles
from core.user.models import CustomUser


# Create your tests here.
class AdminRoleTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.member = CustomUser.objects.create_user(username="new_member", email="email@gmail.com",
                                                     password="testpassword")
        self.user_role = RoleModel.objects.create(user=self.member, company=self.company, role=UserRoles.MEMBER)
        self.admin = CustomUser.objects.create_user(username="admin", email="admin@gmail.com", password="testpassword")
        self.admin_role = RoleModel.objects.create(user=self.admin, company=self.company, role=UserRoles.ADMIN)

    def test_add_admin_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        post_response = self.client.post("/api/companies/appoint-admin/", {
            "user": self.member.id,
            "company": self.company.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.user_role.refresh_from_db()
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(self.user_role.role, UserRoles.ADMIN)

    def test_get_admins_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)
        get_response = self.client.get("/api/companies/admins/",
                                       query_params={"company": self.company.id},
                                       HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(get_response.status_code, 200)
        self.assertIsInstance(get_response.data, list)
        self.assertEqual(len(get_response.data), 1)

    def test_delete_admin_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        post_response = self.client.post("/api/companies/remove-admin/", {
            "user": self.member.id,
            "company": self.company.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.user_role.refresh_from_db()
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(self.user_role.role, UserRoles.MEMBER)
