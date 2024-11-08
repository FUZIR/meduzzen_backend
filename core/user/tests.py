from django.test import TestCase

from .models import CustomUser


# Create your tests here.

class CustomUserModelTest(TestCase):
    def test_image_path_blank(self):
        user = CustomUser.objects.create(username="test_username", email="test_email@gmail.com",
                                         password="somepassword", image_path="")
        self.assertEqual(user.image_path, "")
