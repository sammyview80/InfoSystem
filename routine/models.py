from django.db import models
from collage.models import Semester, Year, Faculty


def get_upload_path(instance, filename):
    # Define the upload path based on the user ID
    return f"data/{instance.name}-{filename}"


class Routine(models.Model):
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
        return f'{self.name}'


class Day(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class BatchSemester(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TeacherWithSubject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Period(models.Model):
    starting_time = models.CharField(max_length=100)
    ending_time = models.CharField(max_length=100)
    teacherName = models.ForeignKey(
        TeacherWithSubject, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.starting_time}/{self.ending_time}-{self.teacherName}'


class AutoMatedRoutine(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    batchSemester = models.ForeignKey(BatchSemester, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    period = models.ManyToManyField(Period)

    def __str__(self):
        return f'{self.day}-{self.batchSemester}-{self.room}-{self.group}-{self.period}'
