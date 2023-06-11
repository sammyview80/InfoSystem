from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RoutineSerializer, AutoMatedRoutineSerializers
from .models import Routine, AutoMatedRoutine
from utils.decorator import with_advance_search


# class GetAllRoutine(APIView):
#     pagination_class = PageNumberPagination
#     serializer_class = RoutineSerializer

#     def get(self, request, format=None):
#         # Get query parameters
#         limit = int(request.query_params.get('limit', 10))
#         type = request.query_params.get('type', '')
#         name = request.query_params.get('name', '')
#         semester = request.query_params.get('semester', '')
#         querys = list(request.query_params.keys())

#         _query_routine_type = [
#             query for query in querys if query in RoutineTypeSerializer().__fields__()]
#         _query_routine = [
#             query for query in querys if query in RoutineSerializer().__fields__()]

#         if len(list(request.query_params.items())) > 0:
#             for key, value in request.query_params.items():
#                 if (key in _query_routine_type):
#                     type_instance = RoutineType.objects.filter(
#                         **{key: value}).values().first()
#                     if type_instance:
#                         instances = Routine.objects.filter(
#                             type=type_instance['id'])
#                 else:
#                     instances = Routine.objects.all()

#         else:
#             instances = Routine.objects.all()

#         # Paginate the results
#         paginator = self.pagination_class()
#         paginated_instances = paginator.paginate_queryset(instances, request)

#         # Serialize paginated instances
#         serializer = self.serializer_class(paginated_instances, many=True)

#         return paginator.get_paginated_response(serializer.data)


class GetAllAutomatedRoutine(APIView):
    pagination_class = PageNumberPagination
    serializer_class = AutoMatedRoutineSerializers

    def get(self, request, format=None):
        @with_advance_search
        def get_advance_search(request, params):
            return request

        filter_conditions = get_advance_search(request,
                                               {'query': ['id', 'day', 'batchSemester', 'room',  'group'  , 'time' ]})

        instances = AutoMatedRoutine.objects.filter(**filter_conditions)

        paginator = self.pagination_class()
        paginated_instances = paginator.paginate_queryset(instances, request)

        serializer = self.serializer_class(paginated_instances, many=True)

        return paginator.get_paginated_response(serializer.data)

class GetAllRoutine(APIView):
    pagination_class = PageNumberPagination
    serializer_class = RoutineSerializer

    def get(self, request, format=None):
        @with_advance_search
        def get_advance_search(request, params):
            return request

        filter_conditions = get_advance_search(request,
                                               {'query': ['type', 'semester', 'year', 'faculty', 'id']})

        instances = Routine.objects.filter(**filter_conditions)

        paginator = self.pagination_class()
        paginated_instances = paginator.paginate_queryset(instances, request)

        serializer = self.serializer_class(paginated_instances, many=True)

        return paginator.get_paginated_response(serializer.data)