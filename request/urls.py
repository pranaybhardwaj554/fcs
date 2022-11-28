from django.urls import path
from .import views


urlpatterns = [
    path('dashboard/reuestp/', views.requestp, name = 'requestp'),
    path('dashboard/reuesth/', views.requesth, name = 'requesth'),
    path('dashboard/requests/', views.requests, name='reuests'),
]