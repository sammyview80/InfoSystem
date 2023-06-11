from django.urls import path, include

from .views import GetAllAutomatedRoutine
urlpatterns = [
    path('getAll/', GetAllAutomatedRoutine.as_view(), name='get-routine'),

]
