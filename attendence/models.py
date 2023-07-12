from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser
from subject.models import SubjectAdd


def attendence_validator(value):
    pass


class Attendence(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.OneToOneField(SubjectAdd, on_delete=models.CASCADE)
    attendence = models.IntegerField(
        default=0, validators=[attendence_validator])

    def __str__(self):
        return f'{self.user}/{self.subject}'
