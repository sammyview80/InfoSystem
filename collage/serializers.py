from rest_framework import serializers
from .models import Year, Semester, Faculty
from subject.serializers import SubjectAddSerializer


class SemesterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Semester
        fields = ['id', 'semester']


class YearSerializer(serializers.ModelSerializer):

    class Meta:
        model = Year
        fields = ['id', 'year']


class FacultySerializer(serializers.ModelSerializer):
    subjects = SubjectAddSerializer()

    class Meta:
        model = Faculty
        fields = ['id', 'faculty', 'subjects']
