from django.db import models
from django.conf import settings
import uuid
import os
from PIL import Image


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


def recipe_image_path(instance, filename):
    ext = filename.split(".")[-1]
    new_path = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/recipe/", new_path)


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    instruction = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    image = models.ImageField(null=True, upload_to=recipe_image_path)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField("Ingredient")
    tags = models.ManyToManyField("Tag")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Recipe, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
