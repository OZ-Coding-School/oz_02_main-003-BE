from django.urls import path
from .views import MainPageView

urlpatterns = [
    # /api/v1/main
    path("", MainPageView.as_view(), name="main-page")
]