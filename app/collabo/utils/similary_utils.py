from collabo.models import RecipeSimilarity
from collabo.utils.interaction_utils import get_recent_interactions
from recipes.models import Recipe
from django.db.models import Case, When

def get_similar_recipes(user_id):
    # 사용자의 최근 상호작용 레시피 ID 목록 가져오기
    recent_recipe_ids = get_recent_interactions(user_id)
    similar_recipes_with_scores = {}
    
    WEIGHTS = [1.5, 1.4, 1.3, 1.2, 1.1]
    for idx, recipe_id in enumerate(recent_recipe_ids):
        # 최근 상호작용일수록 높은 가중치 부여
        similar_recipe_ids = (
            RecipeSimilarity.objects.filter(recipe=recipe_id)
            .values("similar_recipe", "similarity_score")
        )

        for similar_recipe in similar_recipe_ids:
            sim_recipe_id = similar_recipe["similar_recipe"]
            similarity_score = similar_recipe["similarity_score"]
            score = similarity_score * WEIGHTS[idx]
            if score > 0.0:
                print(f"similarity_score: {similarity_score}, weight: {WEIGHTS[idx]}, score: {score}")
            
            if sim_recipe_id in similar_recipes_with_scores:
                similar_recipes_with_scores[sim_recipe_id] += score
            else:
                similar_recipes_with_scores[sim_recipe_id] = score

    sorted_similar_recipe_ids = sorted(similar_recipes_with_scores.keys(), 
                                       key=lambda x: similar_recipes_with_scores[x], 
                                       reverse=True)
    preserved_order = Case(
        *[When(id=pk, then=pos) for pos, pk in enumerate(sorted_similar_recipe_ids)]
    )
    
    similar_recipes = Recipe.objects.filter(id__in=sorted_similar_recipe_ids).order_by(preserved_order)
    return similar_recipes