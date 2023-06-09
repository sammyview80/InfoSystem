from typing import Any
from .models import UserGmailToken
from rest_framework import serializers
from .models import CustomUser
from collage.serializers import SemesterSerializer, YearSerializer, FacultySerializer


class UserSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer()
    year = YearSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name',
                  'password', 'semester', 'year', 'faculty']
        extra_kwargs = {'password': {'write_only': True}, "semester": {
            "error_messages": {"required": "Give yourself a username"}}}


class UserGmailTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGmailToken
        fields = ['user', 'pickle_token', 'credentials']
