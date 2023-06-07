from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


class Semester(models.Model):

    semester = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ], unique=True
    )

    def __str__(self):
        return f'{self.semester}'


class Year(models.Model):
    current_year = datetime.now().year
    YEAR_CHOICES = [(year, str(year))
                    for year in range(2018, current_year + 1)]
    year = models.IntegerField(choices=YEAR_CHOICES)

    def __str__(self):
        return f'{self.year}'


class Faculty(models.Model):
    faculty = models.CharField(max_length=100)

    def __str__(self):
        return self.faculty
