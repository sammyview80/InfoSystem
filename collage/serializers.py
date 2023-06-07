from rest_framework import serializers
from .models import Year, Semester, Faculty


class SemesterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Semester
        fields = ['id', 'semester']


class YearSerializer(serializers.ModelSerializer):

    class Meta:
        model = Year
        fields = ['id', 'year']


class FacultySerializer(serializers.ModelSerializer):

    class Meta:
        model = Faculty
        fields = ['id', 'faculty']
