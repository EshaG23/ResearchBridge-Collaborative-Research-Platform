from django.urls import path
from . import views
app_name = 'profiles'
urlpatterns = [path('', views.edit, name='edit'), path('resumes/<int:pk>/', views.resume_download, name='resume')]
