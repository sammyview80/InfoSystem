from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .serializers import PDFDocumentSerializer, DOCDocumentSerializer, ImageDocumentSerializer, PPTDocumentSerializer
# from fileManager.mail.main import FetchMail, CheckMail
from mail.main import FetchMail, CheckMail
from django.contrib.auth import authenticate, login
import asyncio
import threading
from .models import CustomUser, PDFDocument, DOCDocument, ImageDocument, PPTDocument, XLSXDocument
from collage.models import Semester, Faculty
from django.shortcuts import get_object_or_404
from utils.decorator import with_advance_search


class GetAllPdfView(APIView):
    pagination_class = PageNumberPagination
    serializer_class = PDFDocumentSerializer

    def get(self, request, format=None):
        @with_advance_search
        def get_advance_search(request, params):
            return request

        filter_conditions = get_advance_search(request,
                                               {'query': ['id', 'user', 'semester', 'faculty']})

        instances = PDFDocument.objects.filter(**filter_conditions)

        paginator = self.pagination_class()
        paginated_instances = paginator.paginate_queryset(instances, request)

        serializer = self.serializer_class(paginated_instances, many=True)

        return paginator.get_paginated_response(serializer.data)


class GeAllDocumentView(APIView):
    pagination_class = PageNumberPagination
    serializer_class = DOCDocumentSerializer

    def get(self, request, format=None):
        @with_advance_search
        def get_advance_search(request, params):
            return request

        filter_conditions = get_advance_search(request,
                                               {'query': ['id', 'user', 'semester', 'faculty']})

        instances = DOCDocument.objects.filter(**filter_conditions)

        paginator = self.pagination_class()
        paginated_instances = paginator.paginate_queryset(instances, request)

        serializer = self.serializer_class(paginated_instances, many=True)

        return paginator.get_paginated_response(serializer.data)


class UploadPdfView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.user
        user = CustomUser.objects.filter(email=email).values().first()
        semester = Semester.objects.filter(
            id=user['semester_id']).values().first()
        faculty = Faculty.objects.filter(
            id=user['faculty_id']).values().first()
        pdfSerializer = PDFDocumentSerializer(data=request.data)
        if pdfSerializer.is_valid():
            pdfSerializer.save(user=email)
            return Response({**pdfSerializer.data, 'semester': semester, 'faculty': faculty}, status=status.HTTP_201_CREATED)
        return Response(pdfSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllImageView(APIView):
    pagination_class = PageNumberPagination
    serializer_class = ImageDocumentSerializer

    def get(self, request, format=None):
        @with_advance_search
        def get_advance_search(request, params):
            return request

        filter_conditions = get_advance_search(request,
                                               {'query': ['id', 'user', 'semester', 'faculty']})

        instances = ImageDocument.objects.filter(**filter_conditions)

        paginator = self.pagination_class()
        paginated_instances = paginator.paginate_queryset(instances, request)

        serializer = self.serializer_class(paginated_instances, many=True)

        return paginator.get_paginated_response(serializer.data)
