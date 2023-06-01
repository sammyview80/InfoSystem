from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import os
from django.core.validators import RegexValidator
from collage.models import Semester, Year, Faculty

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)
    



class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, validators=[
            RegexValidator(
                regex=r'^[\w.-]+@nec\.edu\.np$',
                message="Please use NEC email address")
        ])
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    semester = models.OneToOneField(Semester, on_delete=models.CASCADE, null=True)
    year = models.OneToOneField(Year, on_delete=models.CASCADE, null=True)
    faculty = models.OneToOneField(Faculty, on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


def get_upload_path(instance, filename):
    # Define the upload path based on the user ID
    return f"data/{instance.user.id}-{filename}"


class UserGmailToken(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, unique=True)
    pickle_token = models.FileField(
        upload_to=get_upload_path, null=True, blank=True)
    credentials = models.FileField(upload_to=get_upload_path)

    def __str__(self):
        return self.user.email
