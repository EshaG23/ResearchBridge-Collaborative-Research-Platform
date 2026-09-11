from django.urls import path
from . import views
app_name='mentorship'
urlpatterns=[
    path('',views.inbox,name='inbox'),
    path('ideas/<uuid:pk>/',views.suggestions,name='suggestions'),
    path('requests/<int:pk>/',views.review,name='review'),
]
