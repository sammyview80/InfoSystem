from django.urls import path, include

from .views import GetAllRoutine
urlpatterns = [
    path('getAll/', GetAllRoutine.as_view(), name='get-routine'),

]
