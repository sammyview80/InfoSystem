from django.db import models
from collage.models import Semester, Year, Faculty
from users.models import CustomUser


class SubjectAdd(models.Model):
    name = models.CharField(max_length=100, unique=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}-{self.semester}-{self.faculty}'


class Subject(models.Model):
    title = models.OneToOneField(SubjectAdd, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}/{self.user}'
