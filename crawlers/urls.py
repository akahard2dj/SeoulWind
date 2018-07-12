from django.urls import path
from crawlers import views

urlpatterns = [
    path('update_data/', views.update_data),
]
