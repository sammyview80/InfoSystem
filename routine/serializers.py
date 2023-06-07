from .models import Routine, RoutineType
from rest_framework import serializers
from collage.serializers import SemesterSerializer, YearSerializer, FacultySerializer


class RoutineTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoutineType
        fields = "__all__"

    def __fields__(self):
        return ['id', 'name']


class RoutineSerializer(serializers.ModelSerializer):
    type = RoutineTypeSerializer()
    semester = SemesterSerializer()
    year = YearSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = Routine
        fields = ['type', 'name', 'file', 'semester', 'year', 'faculty']
        # read_only_fields = ('type', 'recipient')

    def __fields__(self):
        return ['id', 'type', 'name']
