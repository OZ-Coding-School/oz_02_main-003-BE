from django.urls import path
from .views import IngredientTypeView, IngredientTypeSearchView

urlpatterns = [
    # /api/v1/ingredients/recipes
    path("/<str:type>", IngredientTypeView.as_view(), name="ingredient-type"),
    # /api/v1/ingredients/fridges/%EA%B3
    path("/<str:type>/<str:search>", IngredientTypeSearchView.as_view(), name="ingredient-search"),
]