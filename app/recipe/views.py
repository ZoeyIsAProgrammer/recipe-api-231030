from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from recipe.models import Tag, Ingredient, Recipe
from recipe import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import base64
import json
from django.core.files.base import ContentFile


class BaseRecipeAttrViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin
):
    '''Base class for Tag and Ingredient ViewSets'''
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get("assigned_only", 0)))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False).distinct()
        return queryset.filter(user=self.request.user).all().order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def str_to_int(self, ids_str):
        id_ints = [int(id) for id in ids_str.split(",")]
        return id_ints

    def get_queryset(self):
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset
        if tags:
            tags = self.str_to_int(tags)
            queryset = queryset.filter(tags__in=tags).distinct()
        if ingredients:
            ingredients = self.str_to_int(ingredients)
            queryset = queryset.filter(ingredients__in=ingredients).distinct()
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.RecipeDetailSerializer
        if self.action == "upload_image":
            return serializers.RecipeUploadImageSerializer
        return self.serializer_class

    @action(detail=True, methods=["POST"], url_path="upload-image")
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serialzer = self.get_serializer(recipe, data=request.data)
        if serialzer.is_valid():
            serialzer.save()
            return Response(serialzer.data, status.HTTP_200_OK)
        return Response(serialzer.errors, status.HTTP_400_BAD_REQUEST)
