from django.urls import path
from .views import *

urlpatterns = [
    # /api/v1/collabo
    path("", TestView.as_view(), name="create-recipe"),
]