from django.test import TestCase

from core.request.tests import BaseTestCase

from .models import CustomUser

# Create your tests here.

class CustomUserModelTest(TestCase):
    def test_image_path_blank(self):
        user = CustomUser.objects.create(username="test_username", email="test_email@gmail.com",
                                         password="somepassword", image_path="")
        self.assertEqual(user.image_path, "")

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

        leave_response = self.client.post("/api/users/leave/", HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(leave_response.status_code, 200)
        self.assertIn("detail", leave_response.data)
        self.assertEqual(leave_response.data["detail"], "You successfully leave company")
        self.assertFalse(self.company.members.filter(id=self.member.id).exists())

