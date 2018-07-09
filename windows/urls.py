from django.urls import path
from windows import views

urlpatterns = [
    path('', views.index),
    path('data/current/', views.get_data),
    path('map/current/<data_type>', views.redirect_page),
]
