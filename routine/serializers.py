from rest_framework.fields import empty
from .models import Routine, AutoMatedRoutine, Day, BatchSemester, Room, Group, TeacherWithSubject, Period
from rest_framework import serializers
from collage.serializers import SemesterSerializer, YearSerializer, FacultySerializer
from django.core.exceptions import ValidationError


class RoutineSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer()
    year = YearSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = Routine
        fields = ['id', 'name', 'file', 'semester', 'year', 'faculty']

    def __fields__(self):
        return ['id', 'type', 'name']


class DaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Day
        fields = ['id', 'name']


class BatchSemesterSerializer(serializers.ModelSerializer):

    class Meta:
        model = BatchSemester
        fields = ['id', 'name']


class TeacherWithSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherWithSubject
        fields = ['id', 'name']

        # raise ValidationError('testingsvalidtion')


class PeriodSeriallizer(serializers.ModelSerializer):
    teacherName = serializers.PrimaryKeyRelatedField(
        queryset=TeacherWithSubject.objects.all())
    day = serializers.PrimaryKeyRelatedField(queryset=Day.objects.all())

    def create(self, validated_data):
        try:
            return Period.objects.get(**validated_data)
        except Period.DoesNotExist:
            return super().create(validated_data)
        
    class Meta:
        model = Period
        fields = ['id', 'starting_time', 'ending_time', 'teacherName', 'day']


class PeriodSeriallizerPost(serializers.ModelSerializer):
    teacherName = TeacherWithSubjectSerializer()
    day = DaySerializer()

    class Meta:
        model = Period
        fields = ['id', 'starting_time', 'ending_time', 'teacherName', 'day']


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name']


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ['id', 'name']


class AutoMatedRoutineSerializers(serializers.ModelSerializer):
    day = serializers.PrimaryKeyRelatedField(
        queryset=Day.objects.all())
    batchSemester = serializers.PrimaryKeyRelatedField(
        queryset=BatchSemester.objects.all())
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all())
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all())
    period = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.all(), many=True)

    class Meta:
        model = AutoMatedRoutine
        fields = ['id', 'day', 'batchSemester', 'room', 'group', 'period']

    # def get_period(self, obj):
    #     period_queryset = obj.period.all()
    #     return PeriodSeriallizer(period_queryset, many=True).data


class AutoMatedRoutineSerializersPost(serializers.ModelSerializer):
    day = DaySerializer()
    batchSemester = BatchSemesterSerializer()
    room = RoomSerializer()
    group = GroupSerializer()
    period = serializers.SerializerMethodField()

    class Meta:
        model = AutoMatedRoutine
        fields = ['id', 'day', 'batchSemester', 'room', 'group', 'period']

    def get_period(self, obj):
        period_queryset = obj.period.all()
        return PeriodSeriallizerPost(period_queryset, many=True).data
