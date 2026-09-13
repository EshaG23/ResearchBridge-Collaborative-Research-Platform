from django.urls import path
from . import views
app_name='tasks'
urlpatterns=[path('<uuid:pk>/tasks/',views.board,name='board'),path('<uuid:pk>/tasks/new/',views.edit,name='new'),path('<uuid:pk>/tasks/files/<uuid:file_id>/',views.download,name='download'),path('<uuid:pk>/tasks/<uuid:task_id>/',views.detail,name='detail'),path('<uuid:pk>/tasks/<uuid:task_id>/edit/',views.edit,name='edit'),path('<uuid:pk>/tasks/<uuid:task_id>/<str:action>/',views.action,name='action')]
