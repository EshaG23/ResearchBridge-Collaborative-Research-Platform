from django.urls import path
from . import views
app_name='ip_progress'
urlpatterns=[path('<uuid:pk>/ip/',views.overview,name='overview'),path('<uuid:pk>/ip/files/<uuid:record_id>/',views.download,name='download'),path('<uuid:pk>/ip/achievement/<int:record_id>/withdraw/',views.action,{'action':'withdraw'},name='withdraw'),path('<uuid:pk>/ip/<str:action>/',views.action,name='action')]
