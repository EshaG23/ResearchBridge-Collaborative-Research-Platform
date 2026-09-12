from django.urls import path
from . import views
app_name='recruitment'
urlpatterns=[path('',views.index,name='index'),path('projects/<uuid:project_pk>/',views.index,name='project'),
    path('projects/<uuid:project_pk>/apply/',views.apply,name='apply'),
    path('<uuid:pk>/',views.detail,name='detail'),path('<uuid:pk>/resume/',views.resume,name='resume')]
