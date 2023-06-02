
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import os
from django.core.validators import RegexValidator
from collage.models import Semester, Year, Faculty

from users.models import CustomUser



def get_upload_path(instance, filename):
    # Define the upload path based on the user ID
    return f"data/{instance.user.id}-{filename}"



class DOCDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)

    upload_timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Set the title field with the file name without extension
        self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        print(self.user)
        self.semester = self.user.semester
        self.faculty = self.user.faculty
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PDFDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)

    upload_timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Set the title field with the file name without extension
        self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ImageDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)

    upload_timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Set the title field with the file name without extension
        self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PPTDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path)
    
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)

    upload_timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Set the title field with the file name without extension
        self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class XLSXDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        # Set the title field with the file name without extension
        self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title