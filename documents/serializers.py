from rest_framework import serializers
from .models import DOCDocument, ImageDocument, PDFDocument, PPTDocument, XLSXDocument



class DOCDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = DOCDocument
        fields = ['file', 'user', 'semester', 'faculty']


class PDFDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PDFDocument
        fields = ['file', 'user', 'semester', 'faculty']
        # read_only_fields = ('user', 'semester', 'faculty')


class PPTDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PPTDocument
        fields = ['file', 'user', 'semester', 'faculty']


class XLSXDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = XLSXDocument
        fields = ['file', 'user', 'semester', 'faculty']


class ImageDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageDocument
        fields = ['file', 'user', 'semester', 'faculty']
