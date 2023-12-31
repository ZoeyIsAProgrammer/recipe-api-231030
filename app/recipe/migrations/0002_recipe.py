# Generated by Django 4.2.6 on 2023-11-21 05:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import recipe.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('instruction', models.TextField(blank=True)),
                ('time_minutes', models.IntegerField()),
                ('image', models.ImageField(null=True, upload_to=recipe.models.recipe_image_path)),
                ('ingredients', models.ManyToManyField(to='recipe.ingredient')),
                ('tags', models.ManyToManyField(to='recipe.tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
