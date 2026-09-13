from django.urls import path
from . import views
app_name='accounts'
urlpatterns=[path('demo-session/',views.new_demo_session,name='demo-session'),path('login/',views.sign_in,name='login'),path('forgot-password/',views.forgot,name='forgot'),
 path('verify/',views.verify,name='verify'),path('resend/',views.resend,name='resend'),
 path('reset-password/',views.reset_password,name='reset'),path('logout/',views.sign_out,name='logout')]
