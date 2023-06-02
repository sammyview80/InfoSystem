from django.urls import path, include

from .views import GetAllPdfView, UploadPdfView

urlpatterns = [
    path('pdf/', GetAllPdfView.as_view(), name='get-pdf'),
    path('create/pdf/', UploadPdfView.as_view(), name='create-pdf'),

]
