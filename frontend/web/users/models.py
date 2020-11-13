from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, **extra_fields):
        """
        Create and save a User with the given email.
        """
        if not email:
            raise ValueError(_('Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # Users do not have passwords in this service.
        # We use magic links to login users
        user.set_unusable_password()
        user.save()
        return user

    def get_or_create_user(self, email, **extra_fields):
        """
        Get or Create a User with the given email.
        """
        if not email:
            raise ValueError(_('Email must be set'))
        email = self.normalize_email(email)
        qs = self.model.objects.filter(email=email)
        if qs.exists():
            return qs.get(), False
        user = self.model(email=email, **extra_fields)
        # Users do not have passwords in this service.
        # We use magic links to login users
        user.set_unusable_password()
        user.save()
        return user, True


class User(AbstractUser):
    username = None
    email = EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
