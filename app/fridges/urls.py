from django.urls import path
from .views import FridgeView, FridgeIngredientAddView

urlpatterns = [
    # /api/v1/fridges
    path("", FridgeView.as_view(), name="Fridge-view"),
    # /api/v1/fridges/ingredients
    path("/ingredients", FridgeIngredientAddView.as_view(), name="Fridge-ingredient"),
]
