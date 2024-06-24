from django.urls import path
from .views import CreateRecipe, RecipeRecommendView, RecipeDetailDeleteView, RecipeCategoryListView, RecipeSearchKeywordView, CreateTempImage, RecipeStep

urlpatterns = [
    # /api/v1/recipes
    path("", CreateRecipe.as_view(), name="create-recipe"),
    # /api/v1/recipes/temp
    path("/temp", CreateTempImage.as_view(), name="create-temp-recipe"),
    # /api/v1/recipes/1
    path("/<int:id>", RecipeDetailDeleteView.as_view(), name="detail-recipe"),
    # /api/v1/recipes/category/book
    path("/category/<str:category>", RecipeCategoryListView.as_view(), name="category-recipe"),
    # /api/v1/recipes/search/%EA%B3
    path("/search/<str:keyword>", RecipeSearchKeywordView.as_view(), name="keyword-recipe"),
    # /api/v1/recipes/recommend
    path("/recommend", RecipeRecommendView.as_view(), name="recommend-recipe"),
    # /api/v1/recipes/step/<int:order>
    path("/step/<int:order>", RecipeStep.as_view(), name="recipe-step-delete")
]