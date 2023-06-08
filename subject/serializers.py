from .models import Subject, SubjectAdd
from rest_framework import serializers
from users.serializers import UserSerializer


class SubjectAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectAdd
        fields = ['id', 'name', 'semester', 'faculty', 'year']


class SubjectSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    title = SubjectAddSerializer()

    class Meta:
        model = Subject
        fields = ['id', 'user', 'title']
