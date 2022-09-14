from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("create/<int:room>/", views.CreateReview, name="create"),
]