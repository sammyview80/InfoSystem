from django.urls import path, include

from .views import GetAllPdfView, UploadPdfView, GeAllDocumentView, GetAllImageView

urlpatterns = [
    path('pdf/getAll/', GetAllPdfView.as_view(), name='get-pdf'),
    path('pdf/create/', UploadPdfView.as_view(), name='create-pdf'),
    path('doc/getAll/', GeAllDocumentView.as_view(), name="get-doc"),
    path('image/getAll/', GetAllImageView.as_view(), name="get-image")

]
