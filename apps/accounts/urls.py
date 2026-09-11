from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [path('login/', views.sign_in, name='login'), path('verify/', views.verify, name='verify'),
               path('resend/', views.resend, name='resend'), path('logout/', views.sign_out, name='logout')]
