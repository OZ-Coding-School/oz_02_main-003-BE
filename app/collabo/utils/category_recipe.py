from collabo.models import Interaction, RecipeSimilarity
from collabo.utils.interaction_utils import get_recent_interactions
from recipes.models import Recipe
from django.db.models import Q, Count
import random


def get_similar_recipes(user_id):
    # 사용자의 최근 상호작용 레시피 ID 목록 가져오기
    recent_recipe_ids = get_recent_interactions(user_id)

    similar_recipe_ids = (
        RecipeSimilarity.objects.filter(recipe__in=recent_recipe_ids)
        .order_by("-similarity_score")
        .values_list("similar_recipe", flat=True)
        .distinct()
    )
    similar_recipes = Recipe.objects.filter(id__in=similar_recipe_ids)
    return similar_recipes
