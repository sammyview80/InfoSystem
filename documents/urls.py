from django.urls import path, include

from .views import GetAllPdfView, UploadPdfView, GeAllDocumentView, GetAllImageView, GetAllPPTView, GetAllXLXSView

urlpatterns = [
    path('pdf/getAll/', GetAllPdfView.as_view(), name='get-pdf'),
    path('doc/getAll/', GeAllDocumentView.as_view(), name="get-doc"),
    path('image/getAll/', GetAllImageView.as_view(), name="get-image"),
    path('ppt/getAll/', GetAllPPTView.as_view(), name="get-ppt"),
    path('xlxs/getAll/', GetAllXLXSView.as_view(), name="get-xlxs"),
    path('pdf/create/', UploadPdfView.as_view(), name='create-pdf'),
]
