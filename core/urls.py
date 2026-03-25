from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('scan-ingredients/<int:upload_id>/', views.scan_ingredients, name='scan_ingredients'),
    path('profile/', views.profile, name='profile'),
    path('result/<int:scan_id>/', views.result, name='result'),
]
