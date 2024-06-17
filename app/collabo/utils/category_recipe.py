from collabo.models import Interaction, RecipeSimilarity
from collabo.utils.interaction_utils import get_recent_interactions
from recipes.models import Recipe
from django.db.models import Q, Count
import random

def get_similar_recipes(user_id, category, limit=5):
    # 사용자의 최근 상호작용 레시피 ID 목록 가져오기
    recent_recipe_ids = get_recent_interactions(user_id)

    # 해당 카테고리의 레시피 목록 가져오기
    recipes_category = Recipe.objects.filter(
        id__in=recent_recipe_ids,
        category=category
    )
    all_recipes_category = Recipe.objects.filter(
        category=category
    )

    # RecipeSimilarity 모델에서 유사도 레시피들 가져오기
    similarity_objects = RecipeSimilarity.objects.filter(
        Q(recipe_id__in=[r.id for r in recipes_category]) |
        Q(similar_recipe_id__in=[r.id for r in all_recipes_category])
    ).order_by('-similarity_score')
    # 유사도가 높은 순으로 레시피 목록 생성
    similar_recipes = []
    for similarity in similarity_objects:
        if similarity.recipe_id in [r.id for r in recipes_category]:
            similar_recipes.append(similarity.similar_recipe)
            print(similar_recipes)
        elif similarity.similar_recipe_id in [r.id for r in all_recipes_category]:
            similar_recipes.append(similarity.recipe)
            print(similar_recipes)
        if len(similar_recipes) >= limit:
            break
    # similarity_score가 0인 데이터를 랜덤하게 추출
    zero_score_recipes = RecipeSimilarity.objects.filter(
        Q(recipe_id__in=[r.id for r in all_recipes_category]) |
        Q(similar_recipe_id__in=[r.id for r in all_recipes_category])
    ).filter(similarity_score=0)

    # 유사도가 높은 순으로 정렬된 레시피와 랜덤으로 선택된 zero_score_recipes를 합치기
    similar_recipes += random.sample(list(zero_score_recipes), min(limit - len(similar_recipes), zero_score_recipes.count()))

    return similar_recipes