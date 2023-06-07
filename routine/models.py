from django.db import models
from collage.models import Semester, Year, Faculty


def get_upload_path(instance, filename):
    # Define the upload path based on the user ID
    return f"data/{instance.name}-{filename}"


class RoutineType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Routine(models.Model):

    type = models.ForeignKey(
        RoutineType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    file = models.FileField(upload_to=get_upload_path)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, null=True, blank=True)
    year = models.ForeignKey(
        Year, on_delete=models.CASCADE, null=True, blank=True)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ['name']
        ordering = ['name']

    def __str__(self):
        return f'{self.name}-{self.type}'
