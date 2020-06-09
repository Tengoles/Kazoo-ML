from django.urls import path
from . import views

urlpatterns = [
        path('', views.store_data, name='store_json'),
        path('display_missing/', views.display_missing, name='display-missing-data'),
        path('display_missing/<slug:slug>/', views.display_missing, name='display-missing-data'),
        ]