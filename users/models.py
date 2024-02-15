from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.core.validators import MinLengthValidator



class UserAccountMangement(BaseUserManager):
    def create_user(self,username,email,phone_number,password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not phone_number:
            raise ValueError('Users must have an phone number')
        email=self.normalize_email(email)
        email=email.strip()
        email=email.lower()

        user=self.model(
            username=username,
            email=email,
            phone_number=phone_number 
        )
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self,username,email,phonenumber=None,password=None):
        user=self.create_user(
            username=username,
            email=email,
            phone_number=phonenumber,
            password=password
        )
        user.is_staff=True
        user.is_superuser=True
        user.save()
        return user


class UserAccount(AbstractBaseUser,PermissionsMixin):
    username=models.CharField(max_length=100,validators=[MinLengthValidator(limit_value=3, message="Minimum 3 characters required.")],unique=True)
    email=models.EmailField(max_length=100,unique=True)
    phone_number=models.CharField(max_length=10,unique=True)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)

    objects=UserAccountMangement()


    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','phonenumber']


    def __str__(self):
        return self.email

class PromptInput(models.Model):
    prompt=models.CharField(max_length=300)