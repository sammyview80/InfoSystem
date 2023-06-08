from django.urls import path, include

from .views import GetAllSemester, GetAllYear, GetAllFaculty

urlpatterns = [
    path('semester/getAll', GetAllSemester.as_view(), name='get_all_semester'),
    path('year/getAll', GetAllYear.as_view(), name='get_all_year'),
    path('faculty/getAll', GetAllFaculty.as_view(), name='get_all_faculty'),
]
