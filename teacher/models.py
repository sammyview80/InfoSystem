from django.db import models
from subject.models import SubjectAdd


class Teacher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.ManyToManyField(SubjectAdd, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    abbreviation = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name}'
