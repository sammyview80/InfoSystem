from .models import SubjectAdd
from rest_framework import serializers


class SubjectAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectAdd
        fields = ['id', 'name']
