from django.urls import path
from . import views
app_name = 'notifications'
urlpatterns = [
    path('',views.index,name='index'), path('poll/',views.poll,name='poll'),
    path('read-all/',views.read_all,name='read-all'), path('<int:pk>/read/',views.read,name='read'),
]

