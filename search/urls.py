from django.urls import path
from .import views

urlpatterns = [
    path('dashboard/searchorg/', views.search_org, name = 'search'),
    path('dashboard/searchprofessional/', views.search_professional, name = 'search'),
]