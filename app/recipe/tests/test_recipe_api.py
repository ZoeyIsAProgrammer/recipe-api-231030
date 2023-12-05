from rest_framework.test import APITestCase, APIClient
from recipe.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from collections import OrderedDict
from tempfile import NamedTemporaryFile
from PIL import Image
import os

User = get_user_model()
recipe_list_url = reverse("recipe:recipe-list")


def get_recipe_detail_url(pk):
    return reverse("recipe:recipe-detail", args=[pk])


def get_upload_image_url(pk):
    return reverse("recipe:recipe-upload-image", args=[pk])


def create_recipe(user, **updates):
    defaults = {"title": "recipe", "price": 3.56, "time_minutes": 5}
    defaults.update(updates)
    return Recipe.objects.create(user=user, **defaults)


def create_tag(user, name=None):
    if not name:
        name = "tag"
    return Tag.objects.create(user=user, name=name)


def create_ingredient(user, name=None):
    if not name:
        name = "ingredient"
    return Ingredient.objects.create(user=user, name=name)


class PublicRecipeAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@email.com", password="testing321"
        )
        create_recipe(self.user)

    def test_auth_needed(self):
        """test authentication is needed to access recipe APIs"""
        self.assertEqual(len(Recipe.objects.all()), 1)
        r = self.client.get(recipe_list_url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@email.com", password="testing321"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_recipes(self):
        """test recipe APIs can be accessed with authentication"""
        create_recipe(self.user)
        r = self.client.get(recipe_list_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 1)

    def test_list_recipes_own(self):
        """test one can only access her own recipes"""
        create_recipe(self.user)
        user2 = User.objects.create_user(
            email="testuser2@email.com", password="testing321"
        )
        create_recipe(user2, **{"title": "recipe2"})
        r = self.client.get(recipe_list_url)
        user_recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(user_recipes, many=True)
        self.assertEqual(len(Recipe.objects.all()), 2)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data, serializer.data)

    def test_filter_recipes_by_tags(self):
        """test getting recipes with one of the specified tags"""
        create_tag(user=self.user, name="tag1")
        create_tag(user=self.user, name="tag2")
        create_tag(user=self.user, name="tag3")
        rec1 = create_recipe(user=self.user, **{"title": "recipe1"})
        rec2 = create_recipe(user=self.user, **{"title": "recipe2"})
        rec3 = create_recipe(user=self.user, **{"title": "recipe3"})
        rec1.tags.set([1, 2])
        rec2.tags.set([1, 3])
        rec3.tags.add(3)
        # the below will get recipes with either tag with id 1 or tag with id 2 or both
        r = self.client.get(recipe_list_url, {"tags": "1,2"})
        serializer1 = RecipeSerializer(rec1)
        serializer2 = RecipeSerializer(rec2)
        serializer3 = RecipeSerializer(rec3)
        self.assertIn(serializer1.data, r.data)
        self.assertIn(serializer2.data, r.data)
        self.assertNotIn(serializer3.data, r.data)

    def test_filter_recipes_by_ingredients(self):
        """test getting recipes with one of the specified ingredients"""
        create_ingredient(user=self.user, name="ingredient1")
        create_ingredient(user=self.user, name="ingredient2")
        create_ingredient(user=self.user, name="ingredient3")
        rec1 = create_recipe(user=self.user, **{"title": "recipe1"})
        rec2 = create_recipe(user=self.user, **{"title": "recipe2"})
        rec3 = create_recipe(user=self.user, **{"title": "recipe3"})
        rec1.ingredients.set([1, 2])
        rec2.ingredients.set([1, 3])
        rec3.ingredients.add(3)
        # the below will get recipes with either ingredient with id 1
        # or ingredient with id 2 or both
        r = self.client.get(recipe_list_url, {"ingredients": "1,2"})
        serializer1 = RecipeSerializer(rec1)
        serializer2 = RecipeSerializer(rec2)
        serializer3 = RecipeSerializer(rec3)
        self.assertIn(serializer1.data, r.data)
        self.assertIn(serializer2.data, r.data)
        self.assertNotIn(serializer3.data, r.data)

    def test_create_recipe(self):
        """test creating a basic recipe successfully"""
        payload = {"title": "recipe1", "price": 3.56, "time_minutes": 5}
        r = self.client.post(recipe_list_url, data=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        result = {
            "id": 1,
            "title": "recipe1",
            "instruction": "",
            "price": "3.56",
            "time_minutes": 5,
            "image": None,
            "ingredients": [],
            "tags": [],
        }
        self.assertEqual(dict(r.data), result)

    def test_create_recipe_image(self):
        """test when creating an recipe you can't upload an image"""
        payload = {
            "title": "recipe1",
            "price": 3.56,
            "time_minutes": 5,
            "image": "gobbledygook",
        }
        r = self.client.post(recipe_list_url, data=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data["image"], None)

    def test_create_recipe_tags_ingredients(self):
        """test when creating a recipe you can bind it to some tags and
         ingredients represented by their ids"""
        create_tag(user=self.user, name="tag1")
        create_tag(user=self.user, name="tag2")
        create_ingredient(user=self.user, name="ingredient1")
        create_ingredient(user=self.user, name="ingredient2")
        payload = {
            "title": "recipe",
            "price": 3.56,
            "time_minutes": 5,
            "tags": [1, 2],
            "ingredients": [1, 2],
        }
        r = self.client.post(recipe_list_url, data=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        # check returned tags and ingres data in the response is in the form of
        # a list of ids
        self.assertEqual(r.data["tags"], payload["tags"])
        self.assertEqual(r.data["ingredients"], payload["ingredients"])
        recipe = Recipe.objects.get(id=r.data["id"])
        # check newly created recipe has M2M rel with the specified
        # tags and ingres in payload
        # for some reason two identical QuerySets can't be equal, so use list() here.
        self.assertEqual(list(recipe.tags.all()), list(Tag.objects.all()))
        self.assertEqual(list(recipe.ingredients.all()), list(Ingredient.objects.all()))

    def test_retrieve_recipe(self):
        """test to retrieve detail of a recipe successfully"""
        recipe = create_recipe(self.user)
        r = self.client.get(get_recipe_detail_url(recipe.id))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_retrieve_recipe_tags_ingredients(self):
        """test when retrieving single recipe,
         tags and ingres of it will be shown in detail"""
        create_tag(user=self.user, name="tag1")
        create_tag(user=self.user, name="tag2")
        create_ingredient(user=self.user, name="ingredient1")
        create_ingredient(user=self.user, name="ingredient2")
        recipe = create_recipe(self.user)
        recipe.tags.set([1, 2])
        recipe.ingredients.set([1, 2])
        r = self.client.get(get_recipe_detail_url(recipe.id))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        result = {
            "id": 1,
            "title": "recipe",
            "instruction": "",
            "price": "3.56",
            "time_minutes": 5,
            "image": None,
            "ingredients": [
                OrderedDict([("name", "ingredient1"), ("id", 1)]),
                OrderedDict([("name", "ingredient2"), ("id", 2)]),
            ],
            "tags": [
                OrderedDict([("name", "tag1"), ("id", 1)]),
                OrderedDict([("name", "tag2"), ("id", 2)]),
            ],
        }
        self.assertEqual(dict(r.data), result)

    def test_partial_update_recipe(self):
        recipe = create_recipe(user=self.user)
        recipe.tags.add(create_tag(user=self.user))
        updates = {
            "title": "recipe updated",
            "price": 4.50,
        }
        r = self.client.patch(get_recipe_detail_url(recipe.id), data=updates)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        result = {
            "id": 1,
            "title": updates["title"],
            "instruction": "",
            "price": "{:.2f}".format(updates["price"]),
            "time_minutes": 5,
            "image": None,
            "ingredients": [],
            "tags": [1],
        }
        recipe.refresh_from_db()
        serializer = RecipeSerializer(recipe)
        # check only price and title have been updated and other fields remain as it was
        self.assertEqual(result, dict(serializer.data))

    def test_full_update_recipe(self):
        recipe = create_recipe(user=self.user)
        recipe.tags.add(create_tag(user=self.user))
        recipe.ingredients.add(create_ingredient(user=self.user))
        self.assertEqual(len(recipe.tags.all()), 1)
        self.assertEqual(len(recipe.ingredients.all()), 1)
        updates = {"title": "recipe updated", "price": 4.50, "time_minutes": 10}
        self.client.put(get_recipe_detail_url(recipe.id), data=updates)
        result = {
            "id": 1,
            "title": updates["title"],
            "instruction": "",
            "price": "{:.2f}".format(updates["price"]),
            "time_minutes": updates["time_minutes"],
            "image": None,
            "ingredients": [],
            "tags": [],
        }
        recipe.refresh_from_db()
        serializer = RecipeSerializer(recipe)
        self.assertEqual(result, dict(serializer.data))
        self.assertEqual(len(recipe.tags.all()), 0)
        self.assertEqual(len(recipe.ingredients.all()), 0)

    def test_delete_recipe(self):
        recipe = create_recipe(user=self.user)
        self.assertEqual(len(self.user.recipe_set.all()), 1)
        r = self.client.delete(get_recipe_detail_url(recipe.id))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(self.user.recipe_set.all()), 0)


class ImageUploadingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@email.com", password="testing321"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)
        self.url = get_upload_image_url(self.recipe.id)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """test uploading image to recipe successfully,
         with an image file as value of the image field in request"""
        self.assertTrue(self.recipe.image == None)  # now image is None
        with NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new(mode="RGB", size=(20, 20))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            r = self.client.post(self.url, data={"image": ntf}, format="multipart")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertTrue(
            os.path.exists(self.recipe.image.path)
        )  # the path to the image exists
        self.assertFalse(self.recipe.image == None)  # now image is not None

    def test_bad_request(self):
        """test value for the image field in request must be an image file
         rather than other things e.g. text"""
        r = self.client.post(
            self.url, data={"image": "not a image file"}, format="multipart"
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
