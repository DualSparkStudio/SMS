from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for TextGuard platform."""

    email = models.EmailField(unique=True)
    is_admin_user = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email
