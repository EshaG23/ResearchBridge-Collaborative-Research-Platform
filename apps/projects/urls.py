from django.urls import path
from . import views
app_name = 'projects'
urlpatterns = [
    path('',views.index,name='index'),
    path('create/',views.edit,name='create'),
    path('<uuid:pk>/',views.detail,name='detail'),
    path('<uuid:pk>/edit/',views.edit,name='edit'),
    path('<uuid:pk>/private/',views.private,name='private'),
]

