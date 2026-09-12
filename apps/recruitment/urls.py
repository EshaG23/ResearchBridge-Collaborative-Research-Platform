from django.urls import path
from . import views,review_views
app_name='recruitment'
urlpatterns=[path('<uuid:pk>/decision/',review_views.decision,name='decision'),
    path('<uuid:pk>/meeting/',review_views.meeting,name='meeting'),
    path('meetings/<uuid:pk>/cancel/',review_views.cancel,name='cancel-meeting'),path('',views.index,name='index'),path('projects/<uuid:project_pk>/',views.index,name='project'),
    path('projects/<uuid:project_pk>/apply/',views.apply,name='apply'),
    path('<uuid:pk>/',views.detail,name='detail'),path('<uuid:pk>/resume/',views.resume,name='resume')]
