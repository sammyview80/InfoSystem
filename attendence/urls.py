from django.urls import path, include

from .views import GetAllAttendence
urlpatterns = [
    path('getAll/', GetAllAttendence.as_view(), name='get-routine'),

]
