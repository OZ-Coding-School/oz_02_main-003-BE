from rest_framework.views import APIView
from rest_framework.response import Response
from recipes.models import Recipe
from .serializers import RecipeSerializer
from bookmarks.models import Bookmark
from likes.models import Like
from django.db.models import Count, Q

class MainPageView(APIView):
    # 사용자가 레시피를 좋아하는지 확인 -1 or 1
    def get_user_like_status(self, recipe_id, user_id):
        like_status = Like.objects.filter(recipe_id=recipe_id, user_id=user_id).exists()
        return 1 if like_status else -1

    # 좋아요 수 가장 많은 것
    def get_best_recipes(self, user_id):
        best_recipes = Recipe.objects.annotate(
            likes_count=Count("like"),
        ).order_by(
            "-likes_count"
        )[:1]

        for recipe in best_recipes:
            recipe.like_status = self.get_user_like_status(recipe.id, user_id)

        return best_recipes

    # 북마크된 레시피 중  베에스트
    def get_best_bookmarked_recipes(self, user_id):
        best_bookmarked_recipes = Recipe.objects.annotate(
            bookmarks_count=Count("bookmark"),
        ).order_by("-bookmarks_count")[:1]

        for recipe in best_bookmarked_recipes:
            recipe.like_status = self.get_user_like_status(recipe.id, user_id)

        return best_bookmarked_recipes

    # 특정 카테고리의 레시피를 가져옴
    def get_category_recipes(self, user_id, category_id):
        category_recipes = Recipe.objects.filter(category=category_id).annotate(
            likes_count=Count("like", distinct=True),
            bookmarks_count=Count("bookmark", distinct=True),
        )[:4]

        for recipe in category_recipes:
            recipe.like_status = self.get_user_like_status(recipe.id, user_id)

        return category_recipes

    # 모든 데이터를 반환하는 메인 GET 메소드
    def get(self, request):
        user_id = 4  

        best_recipes = self.get_best_recipes(user_id)
        best_serializer = RecipeSerializer(best_recipes, many=True)

        best_bookmarked_recipes = self.get_best_bookmarked_recipes(user_id)
        best_bookmarked_serializer = RecipeSerializer(
            best_bookmarked_recipes, many=True
        )

        daily_recipes = self.get_category_recipes(user_id, category_id=1)
        daily_serializer = RecipeSerializer(daily_recipes, many=True)

        healthy_recipes = self.get_category_recipes(user_id, category_id=2)
        healthy_serializer = RecipeSerializer(healthy_recipes, many=True)

        desert_recipes = self.get_category_recipes(user_id, category_id=3)
        desert_serializer = RecipeSerializer(desert_recipes, many=True)

        midnight_snack_recipes = self.get_category_recipes(user_id, category_id=4)
        midnight_snack_serializer = RecipeSerializer(midnight_snack_recipes, many=True)

        return Response(
            {
                "status": 200,
                "message": "조회 성공",
                "data": {
                    "best": best_serializer.data,
                    "bestBookmarked": best_bookmarked_serializer.data,
                    "daily": daily_serializer.data,
                    "healthy": healthy_serializer.data,
                    "desert": desert_serializer.data,
                    "midnightSnack": midnight_snack_serializer.data,
                },
            }
        )
