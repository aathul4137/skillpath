from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="roadmap_home"),
    path("roadmap/<int:pk>/", views.result, name="roadmap_result"),
]
