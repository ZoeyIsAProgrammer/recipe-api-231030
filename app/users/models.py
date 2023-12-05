from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Creates custom user model"""

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user in DB"""
        if not email:
            raise ValueError("Users must have an email address to sign in")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create and Save a new admin user"""

        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return f"{self.email}, {self.id}"


# class CustomUser(AbstractUser):
#     email = models.EmailField('email address', unique=True)
#     name = models.CharField(max_length=255)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ('username',)

#     objects = CustomUserManager()
