from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import MinLengthValidator


class UserAccountManager(BaseUserManager):
    """
    Custom manager for UserAccount model.
    """

    def create_user(self, username, email, phone_number, password=None):
        """
        Create a regular user.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not phone_number:
            raise ValueError('Users must have a phone number')
        email = self.normalize_email(email)
        email = email.strip()
        email = email.lower()

        user = self.model(
            username=username,
            email=email,
            phone_number=phone_number
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, phone_number=None, password=None):
        """
        Create a superuser.
        """
        user = self.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email as the unique identifier.
    """

    username = models.CharField(max_length=100, validators=[MinLengthValidator(limit_value=3, message="Minimum 3 characters required.")])
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile = models.ImageField(null=True, blank=True, upload_to='images/')
    is_listed = models.BooleanField(default=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number','username']

    class Meta:
        ordering = ['id']



class PromptInput(models.Model):
    """
    Model for storing prompts.
    """

    prompt = models.CharField(max_length=300)
