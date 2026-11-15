from django.urls import path

from planner import views

urlpatterns = [
    path("health", views.health),
    path("places", views.places),
    path("plans", views.plans),
]
