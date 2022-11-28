from django.urls import path
from .import views

urlpatterns = [
    path('register/', views.register, name = 'register'),
    path('register_user/', views.register_user, name = 'register_user'),
    path('register_org/', views.register_org, name = 'register_org'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('profile/', views.profile, name = 'profile'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('otp/', views.otp, name='otp'),
    path('', views.index, name = 'index')
]