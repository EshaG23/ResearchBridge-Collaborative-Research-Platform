from django.urls import path
from . import views
app_name='communities'
urlpatterns=[path('projects/<uuid:pk>/create/',views.create,name='create'),path('<uuid:pk>/',views.detail,name='detail'),path('<uuid:pk>/leader/',views.leader,name='leader'),path('<uuid:pk>/<str:section>/',views.section,name='section')]
