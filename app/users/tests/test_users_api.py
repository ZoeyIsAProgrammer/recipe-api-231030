from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from freezegun import freeze_time

User = get_user_model()


class CreateUserTests(APITestCase):
    """test creating a user, which does not need authentication"""

    def test_create_user(self):
        """test user created successfully,
        and check "password" field is not in response"""
        payload = {
            "email": "testuser@email.com",
            "name": "testuser",
            "password": "testing321",
        }
        create_url = reverse("users:create")
        r = self.client.post(create_url, payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(**r.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", r.data)

    def test_password_too_short(self):
        """test password must be more than 8 chars"""
        create_url = reverse("users:create")
        payload = {
            "email": "testuser@email.com",
            "name": "testuser",
            "password": "1234567",
        }
        r = self.client.post(create_url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="testuser@email.com").exists())

        payload = {
            "email": "testuser5@email.com",
            "name": "testuser",
            "password": "12345678",
        }
        r = self.client.post(create_url, payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)


class TokenTests(APITestCase):
    """test getting tokens and use them to authenticate with protected views"""

    @freeze_time("2023-01-01 00:00:00")
    def test_token(self):
        # test creating a token pair successfully
        self.user = User.objects.create_user(
            email="testuser@email.com", name="testuser", password="testing321"
        )
        token_url = reverse("users:token_obtain_pair")
        payload = {"email": self.user.email, "password": "testing321"}
        token_r = self.client.post(token_url, payload)
        self.assertEqual(token_r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(token_r.data), 2)
        self.assertIn("refresh", token_r.data)
        self.assertIn("access", token_r.data)

        # test the access token obtained in this way can be used to
        #  authenticate with protected views
        manage_url = reverse("users:manage")
        manage_r = self.client.get(
            manage_url, HTTP_AUTHORIZATION=f'Bearer {token_r.data["access"]}'
        )
        self.assertEqual(manage_r.status_code, status.HTTP_200_OK)

        # test after 60 mins the access token expires
        with freeze_time("2023-01-01 01:00:01"):
            manage_r2 = self.client.get(
                manage_url, HTTP_AUTHORIZATION=f'Bearer {token_r.data["access"]}'
            )
            self.assertEqual(manage_r2.status_code, status.HTTP_401_UNAUTHORIZED)

            # test using the refresh token endpoint to get a new access token
            refresh_url = reverse("users:token_refresh")
            refresh_r = self.client.post(
                refresh_url, {"refresh": token_r.data["refresh"]}
            )
            self.assertEqual(refresh_r.status_code, status.HTTP_200_OK)
            self.assertIn("access", refresh_r.data)
            manage_r3 = self.client.get(
                manage_url, HTTP_AUTHORIZATION=f'Bearer {refresh_r.data["access"]}'
            )
            self.assertEqual(manage_r3.status_code, status.HTTP_200_OK)

        # test after 1 day the refresh token expires too
        with freeze_time("2023-01-02 00:00:01"):
            refresh_r2 = self.client.post(
                refresh_url, {"refresh": token_r.data["refresh"]}
            )
            self.assertEqual(refresh_r2.status_code, status.HTTP_401_UNAUTHORIZED)
            result = {
                "detail": "Token is invalid or expired",
                "code": "token_not_valid",
            }
            self.assertEqual(refresh_r2.data, result)


class ManageUserTests(APITestCase):
    """test retrieve, update, delete an existing user, which needs authentication"""

    def setUp(self):
        self.user = User.objects.create_user(email="testuser", password="testing321")
        self.client = APIClient()

    def test_retrieve_user(self):
        """test user has to be authenticated to retrieve her own user info"""
        manage_url = reverse("users:manage")
        r = self.client.get(manage_url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.user)
        r = self.client.get(manage_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["email"], self.user.email)

    def test_update_user(self):
        """test how user can update her own user info
        and has to be authenticated for it"""
        manage_url = reverse("users:manage")
        payload = {"name": "updated_testuser"}
        r = self.client.patch(manage_url, data=payload)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.user)
        r = self.client.patch(manage_url, data=payload)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["name"], payload["name"])
        self.assertEqual(r.data["email"], self.user.email)
        self.assertEqual(r.data["id"], self.user.id)

    def test_delete_user(self):
        """test user can delete her account and has to be authenticated for it"""
        manage_url = reverse("users:manage")
        r = self.client.delete(manage_url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.user)
        r = self.client.delete(manage_url)
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
