from .models import Attendence
from rest_framework import serializers
from users.serializers import UserSerializer
from subject.serializers import SubjectSerializer


class AttendenceSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    subject = SubjectSerializer()

    class Meta:
        model = Attendence
        fields = ['id', 'user', 'subject', 'attendence']
