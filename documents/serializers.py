from rest_framework import serializers
from .models import DOCDocument, ImageDocument, PDFDocument, PPTDocument, XLSXDocument
from users.serializers import UserSerializer
from collage.serializers import SemesterSerializer, FacultySerializer


class DOCDocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    semester = SemesterSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = DOCDocument
        fields = ['file', 'user', 'semester', 'faculty']


class PDFDocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    semester = SemesterSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = PDFDocument
        fields = ['file', 'user', 'semester', 'faculty']
        # read_only_fields = ('user', 'semester', 'faculty')


class PPTDocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    semester = SemesterSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = PPTDocument
        fields = ['file', 'user', 'semester', 'faculty']


class XLSXDocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    semester = SemesterSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = XLSXDocument
        fields = ['file', 'user', 'semester', 'faculty']


class ImageDocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    semester = SemesterSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = ImageDocument
        fields = ['file', 'user', 'semester', 'faculty']
