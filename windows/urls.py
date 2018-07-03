from django.urls import path
from windows import views

urlpatterns = [
    path('', views.index)
]
