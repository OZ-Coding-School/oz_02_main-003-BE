from django.urls import path
from .views import SaveRecipeSimilarView

urlpatterns = [
    # /api/v1/collabo
    path("", SaveRecipeSimilarView.as_view(), name="create-recipe"),
]