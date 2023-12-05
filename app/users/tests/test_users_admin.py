from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserAdminTests(TestCase):
    """test the organization of the user admin pages follows my configs"""

    def setUp(self):
        self.superuser = User.objects.create_superuser("s@email.com", "testing321")
        self.client.force_login(self.superuser)

    def test_user_listing_page(self):
        """test the user listing page has "email", "name", "id" 3 columns diplayed"""
        user_listing_url = reverse("admin:users_customuser_changelist")
        r = self.client.get(user_listing_url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.superuser.email)
        self.assertContains(r, self.superuser.name)
        self.assertContains(r, self.superuser.id)

    def test_user_change_page(self):
        """test that the user edit page works"""
        url = reverse("admin:users_customuser_change", args=[self.superuser.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_create_user_page(self):
        """test create user page"""
        url = reverse("admin:users_customuser_add")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
