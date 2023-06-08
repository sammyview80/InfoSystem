from .serializers import SemesterSerializer, YearSerializer, FacultySerializer

from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Semester, Year, Faculty
from utils.decorator import with_advance_search


class GetAllSemester(APIView):
    pagination_class = PageNumberPagination
    serializer_class = SemesterSerializer

    def get(self, request, format=None):
        @with_advance_search
        def get_advance_search(request, params):
            return request

        filter_conditions = get_advance_search(request,
                                               {'query': ['id', 'semester']})

        instances = Semester.objects.filter(**filter_conditions)

        paginator = self.pagination_class()
        paginated_instances = paginator.paginate_queryset(instances, request)

        serializer = self.serializer_class(paginated_instances, many=True)

        return paginator.get_paginated_response(serializer.data)


class GetAllYear(APIView):
    pagination_class = PageNumberPagination
    serializer_class = YearSerializer

    def get(self, request, format=None):
        @with_advance_search
        def get_advance_search(request, params):
            return request

        filter_conditions = get_advance_search(request,
                                               {'query': ['id', 'year']})

        instances = Year.objects.filter(**filter_conditions)

        paginator = self.pagination_class()
        paginated_instances = paginator.paginate_queryset(instances, request)

        serializer = self.serializer_class(paginated_instances, many=True)

        return paginator.get_paginated_response(serializer.data)


class GetAllFaculty(APIView):
    pagination_class = PageNumberPagination
    serializer_class = FacultySerializer

    def get(self, request, format=None):
        @with_advance_search
        def get_advance_search(request, params):
            return request

        filter_conditions = get_advance_search(request,
                                               {'query': ['id', 'faculty']})

        instances = Faculty.objects.filter(**filter_conditions)

        paginator = self.pagination_class()
        paginated_instances = paginator.paginate_queryset(instances, request)

        serializer = self.serializer_class(paginated_instances, many=True)

        return paginator.get_paginated_response(serializer.data)
