from django.urls import path
from .views import LikeToggleView

urlpatterns = [
    # /api/v1/likes
    path("", LikeToggleView.as_view(), name="Like-toggle"),
]