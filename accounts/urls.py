from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('doctor-login/', views.doctor_login, name='doctor_login'),
    path('patient-signup/', views.patient_signup, name='patient_signup'),
    path('doctor-signup/', views.doctor_signup, name='doctor_signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]