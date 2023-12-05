from rest_framework.test import APIClient, APITestCase
from recipe.models import Tag, Ingredient, Recipe
from recipe.serializers import TagSerializer, IngredientSerializer
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()
tags_url = reverse("recipe:tag-list")
ingredients_url = reverse("recipe:ingredient-list")


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


class PublicAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_tags_auth_needed(self):
        '''test when accessing the tags url, auth is needed'''
        r = self.client.get(tags_url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ingredients_auth_needed(self):
        '''test when accessing the ingredients url, auth is needed'''
        r = self.client.get(ingredients_url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@email.com", password="testing321"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_tags(self):
        '''test listing tags successfully and one can only access her own tags'''
        tag1 = create_tag(user=self.user, name="tag1")
        user2 = User.objects.create_user(
            email="testuser2@email.com", password="testing321"
        )
        tag2 = create_tag(user=user2, name="tag2")
        serializer1 = TagSerializer([tag1], many=True)
        serializer2 = TagSerializer([tag2], many=True)
        r = self.client.get(tags_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data, serializer1.data)
        self.assertNotEqual(r.data, serializer2.data)

    def test_list_tags_assigned_only(self):
        '''test one can list only tags that have been assigned to a recipe
         by specifying the assigned_only param as a non-zero number'''
        recipe = create_recipe(user=self.user)
        tag1 = create_tag(user=self.user, name="tag1")
        tag1.recipe_set.add(recipe)
        tag2 = create_tag(user=self.user, name="tag2")
        r = self.client.get(tags_url, {"assigned_only": 1})
        serializer1 = TagSerializer([tag1], many=True)
        serializer2 = TagSerializer([tag2], many=True)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data, serializer1.data)
        self.assertNotEqual(r.data, serializer2.data)

    def test_list_tags_assigned_distinct(self):
        '''when a tag has over 2 recipes associated, and when you request
         the assigned tags, that tag can be return over 1 time.
         So test in this case only one same tag is returned'''
        tag1 = create_tag(user=self.user, name='tag1')
        create_tag(user=self.user, name='tag2')
        recipe1 = create_recipe(user=self.user, **{'title': 'recipe1'})
        recipe2 = create_recipe(user=self.user, **{'title': 'recipe2'})
        tag1.recipe_set.set([recipe1, recipe2])
        r = self.client.get(tags_url, {'assigned_only': 1})
        self.assertEqual(r.data, TagSerializer([tag1], many=True).data)
        self.assertEqual(len(r.data), 1)

    def test_create_tag(self):
        r = self.client.post(tags_url, {"name": "test_tag"})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.get(id=r.data['id']).user, self.user)

    def test_list_ingredients(self):
        '''test listing ingredients successfully and one can only access
         her own ingredients'''
        ingredient1 = create_ingredient(user=self.user, name="ingredient1")
        user2 = User.objects.create_user(
            email="testuser2@email.com", password="testing321"
        )
        ingredient2 = create_ingredient(user=user2, name="ingredient2")
        serializer1 = IngredientSerializer([ingredient1], many=True)
        serializer2 = IngredientSerializer([ingredient2], many=True)
        r = self.client.get(ingredients_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data, serializer1.data)
        self.assertNotEqual(r.data, serializer2.data)

    def test_list_ingredients_assigned_only(self):
        '''test one can list only ingredients that have been assigned to a
         recipe by specifying the assigned_only param as a non-zero integer'''
        recipe = create_recipe(user=self.user)
        ingredient1 = create_ingredient(user=self.user, name="ingredient1")
        ingredient1.recipe_set.add(recipe)
        ingredient2 = create_ingredient(user=self.user, name="ingredient2")
        r = self.client.get(ingredients_url, {"assigned_only": "1"})
        serializer1 = IngredientSerializer([ingredient1], many=True)
        serializer2 = IngredientSerializer([ingredient2], many=True)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data, serializer1.data)
        self.assertNotEqual(r.data, serializer2.data)

    def test_list_ingredients_assigned_distinct(self):
        '''when a ingredient has over 2 recipes associated, and when you request
         the assigned ingredients, that ingredient can be return over 1 time.
         So test in this case only one same ingredient is returned'''
        ingredient1 = create_ingredient(user=self.user, name='ingredient1')
        create_ingredient(user=self.user, name='ingredient2')
        recipe1 = create_recipe(user=self.user, **{'title': 'recipe1'})
        recipe2 = create_recipe(user=self.user, **{'title': 'recipe2'})
        ingredient1.recipe_set.set([recipe1, recipe2])
        r = self.client.get(ingredients_url, {'assigned_only': 1})
        self.assertEqual(r.data, IngredientSerializer([ingredient1], many=True).data)
        self.assertEqual(len(r.data), 1)

    def test_create_ingredient(self):
        r = self.client.post(ingredients_url, {"name": "test_ingredient"})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ingredient.objects.get(id=r.data['id']).user, self.user)
