from collabo.models import RecipeSimilarity
from collabo.utils.interaction_utils import get_recent_interactions
from recipes.models import Recipe, Updated_recipe
from django.db.models import Case, When, Count, F, Q


def get_sorted_recipes_without_similar(queryset):
    return queryset.annotate(
        like_count=Count("like", filter=Q(like__recipe_id=F("id"))),
        comment_count=Count("comment", filter=Q(comment__recipe_id=F("id"))),
        bookmark_count=Count("bookmark", filter=Q(bookmark__recipe_id=F("id"))),
        total_interaction=F("like_count") + F("comment_count") + F("bookmark_count"),
    ).order_by("-total_interaction")


def get_category_recipes(category_name):
    """
    해당 카테고리의 레시피를 상호작용 수 기준으로 정렬하여 반환합니다.
    """
    return (
        Recipe.objects.filter(category=category_name)
        .annotate(
            like_count=Count("like", filter=Q(like__recipe_id=F("id"))),
            comment_count=Count("comment", filter=Q(comment__recipe_id=F("id"))),
            bookmark_count=Count("bookmark", filter=Q(bookmark__recipe_id=F("id"))),
            total_interaction=F("like_count")
            + F("comment_count")
            + F("bookmark_count"),
        )
        .order_by("-total_interaction")
    )


def get_recommend_recipes(user_id,):
    # 사용자의 최근 상호작용 레시피 ID 목록 가져오기
    recent_recipe_ids = get_recent_interactions(user_id)
    similar_recipes_with_scores = {}
    if recent_recipe_ids:
        WEIGHTS = [1.5, 1.4, 1.3, 1.2, 1.1]
        for idx, recipe_id in enumerate(recent_recipe_ids):
            # 최근 상호작용일수록 높은 가중치 부여
            similar_recipe_ids = RecipeSimilarity.objects.filter(
                recipe=recipe_id
            ).values("similar_recipe", "similarity_score")

            for similar_recipe in similar_recipe_ids:
                sim_recipe_id = similar_recipe["similar_recipe"]
                similarity_score = similar_recipe["similarity_score"]
                score = similarity_score * WEIGHTS[idx]

                if sim_recipe_id in similar_recipes_with_scores:
                    similar_recipes_with_scores[sim_recipe_id] += score
                else:
                    similar_recipes_with_scores[sim_recipe_id] = score

        sorted_similar_recipe_ids = sorted(
            similar_recipes_with_scores.keys(),
            key=lambda x: similar_recipes_with_scores[x],
            reverse=True,
        )
        preserved_order = Case(
            *[When(id=pk, then=pos) for pos, pk in enumerate(sorted_similar_recipe_ids)]
        )
        similar_recipes = Recipe.objects.filter(
            id__in=sorted_similar_recipe_ids
        ).order_by(preserved_order)

        updated_recipe_ids = Updated_recipe.objects.filter(done=False).values_list(
            "recipe", flat=True
        )

        # 혹시 모를 겹치는 부분 제거
        updated_recipes = Recipe.objects.filter(id__in=updated_recipe_ids).exclude(
            id__in=sorted_similar_recipe_ids
        )
        # similar_recipe += Recipe.objects.filter(id__in)
        return similar_recipes, get_sorted_recipes_without_similar(updated_recipes)
    else:
        return get_sorted_recipes_without_similar(Recipe.objects.all()), None
