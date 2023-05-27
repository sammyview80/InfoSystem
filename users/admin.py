from django.contrib import admin
from .models import CustomUser, DOCDocument, PDFDocument, ImageDocument, PPTDocument, XLSXDocument

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(DOCDocument)
admin.site.register(PDFDocument)
admin.site.register(ImageDocument)
admin.site.register(PPTDocument)
admin.site.register(XLSXDocument)
