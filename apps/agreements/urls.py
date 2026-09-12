from django.urls import path
from . import views
app_name='agreements'
urlpatterns=[path('projects/<uuid:pk>/',views.project,name='project'),path('projects/<uuid:pk>/sign/',views.sign,name='sign'),path('projects/<uuid:pk>/blank/',views.blank,name='blank'),path('projects/<uuid:pk>/enroll-proposer/',views.enroll,name='enroll'),path('<uuid:pk>/',views.evidence,name='evidence'),path('<uuid:pk>/download/',views.download,name='download'),path('<uuid:pk>/verify/',views.verify,name='verify')]
