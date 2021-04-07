from django.urls import path
from . import views
from dashboard.dash_apps.finished_apps import salesapp

urlpatterns = [
    path('', views.home, name="home")
]