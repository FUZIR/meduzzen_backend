
from core.request.tests import BaseTestCase
from core.role.models import RoleModel, UserRoles
from core.user.models import CustomUser


# Create your tests here.
class AdminRoleTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.member = CustomUser.objects.create_user(username="new_member", email="email@gmail.com", password="testpassword")
        self.user_role = RoleModel.objects.create(user=self.member, company=self.company, role=UserRoles.MEMBER)

    def test_add_admin_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        post_response = self.client.post("/api/companies/appoint_admin/", {
            "user": self.member.id,
            "company": self.company.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.user_role.refresh_from_db()
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(self.user_role.role, UserRoles.ADMIN)


    def test_delete_admin_success(self):
        token = self.login_user(self.owner.email, "testpassword")
        self.assertIsNotNone(token)

        post_response = self.client.post("/api/companies/remove_admin/", {
            "user": self.member.id,
            "company": self.company.id
        }, content_type="application/json", HTTP_AUTHORIZATION=f"Token {token}", follow=True)

        self.user_role.refresh_from_db()
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(self.user_role.role, UserRoles.MEMBER)