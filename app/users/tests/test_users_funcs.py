from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFunctionsTests(TestCase):
    """test the customized functions I altered on user model"""

    def test_create_with_email(self):
        """test email is needed when creating a user and will raise error otherwise"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None)

        user = User.objects.create_user(
            email="testuser@email.com", password="testing321"
        )
        self.assertEqual(user.email, "testuser@email.com")
        self.assertTrue(user.check_password("testing321"))

    def test_create_superuser(self):
        """test successfully creating a superuser with email and password"""
        s_user = User.objects.create_superuser(
            email="superuser@email.com", password="testing321"
        )
        self.assertTrue(s_user.is_staff)
        self.assertTrue(s_user.is_superuser)

    def test_email_normalized(self):
        """test email is normalized when creating a user"""
        email = "testuser@eMAiLGB.com"
        user = User.objects.create_user(email, "testing321")
        self.assertEqual(user.email, email.lower())
