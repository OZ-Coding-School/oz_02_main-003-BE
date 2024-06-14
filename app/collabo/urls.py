from django.urls import path
from .views import TestView

urlpatterns = [
    # /api/v1/collabo
    path("", TestView.as_view(), name="create-recipe"),
]