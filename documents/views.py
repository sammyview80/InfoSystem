from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .serializers import PDFDocumentSerializer
# from fileManager.mail.main import FetchMail, CheckMail
from mail.main import FetchMail, CheckMail
from django.contrib.auth import authenticate, login
import asyncio
import threading
from .models import CustomUser, PDFDocument
from collage.models import Semester, Faculty
from django.shortcuts import get_object_or_404

class UploadPdfView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        pdfInstance = PDFDocument.objects.filter(user=user)
        pdfSerializers = PDFDocumentSerializer(pdfInstance, many=True)
        return Response(pdfSerializers.data, status=status.HTTP_200_OK)
    

class GetAllPdfView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        email = request.user
        user =  CustomUser.objects.filter(email=email).values().first()
        semester = Semester.objects.filter(id=user['semester_id']).values().first()
        faculty = Faculty.objects.filter(id=user['faculty_id']).values().first()
        pdfSerializer = PDFDocumentSerializer(data=request.data)
        if pdfSerializer.is_valid():
            pdfSerializer.save(user=email)
            return Response({**pdfSerializer.data, 'semester': semester, 'faculty': faculty}, status=status.HTTP_201_CREATED)
        return Response(pdfSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        