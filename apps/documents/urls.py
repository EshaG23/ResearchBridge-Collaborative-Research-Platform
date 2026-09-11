from django.urls import path
from . import views
app_name = 'documents'
urlpatterns = [
    path('<uuid:project_pk>/upload/',views.upload,name='upload'),
    path('<uuid:project_pk>/<uuid:document_pk>/versions/new/',views.upload,name='version'),
    path('<uuid:project_pk>/versions/<uuid:pk>/',views.download,name='download'),
]

