from rest_framework.views import APIView
from rest_framework.response import Response
from recipes.models import Recipe
from .serializers import RecipeSerializer
from bookmarks.models import Bookmark
from likes.models import Like
from django.db.models import Count
from users.models import User 
from rest_framework import status

class MainPageView(APIView):
    # 사용자가 특정 레시피를 좋아하는지 확인하여 -1 또는 1을 반환하는 메서드
    def get_user_like_status(self, recipe_id, user_id):
        like_status = Like.objects.filter(recipe_id=recipe_id, user_id=user_id).exists()
        return 1 if like_status else -1
    
    # 사용자가 특정 레시피를 북마크했는지 확인하여 -1 또는 1을 반환하는 메서드
    def get_user_bookmark_status(self, recipe_id, user_id):
        bookmark_status = Bookmark.objects.filter(recipe_id=recipe_id, user_id=user_id).exists()
        return 1 if bookmark_status else -1

    # 사용자의 성별(gender)과 나이(age) 정보가 있는지 확인하여 상세 정보 상태를 반환하는 메서드
    def get_user_detail_status(self, user):
        return 1 if user.gender is not None and user.age is not None else -1

    # 좋아요 수가 가장 많은 레시피를 가져오는 메서드
    def get_best_recipes(self, user_id):
        best_recipes = Recipe.objects.annotate(
            likes_count=Count("like"),
        ).order_by(
            "-likes_count"
        )[:1]

        # 각 레시피에 대해 사용자의 좋아요 상태를 설정
        for recipe in best_recipes:
            recipe.like_status = self.get_user_like_status(recipe.id, user_id)

        return best_recipes

    # 북마크된 레시피 중 가장 인기 있는 레시피를 가져오는 메서드
    def get_best_bookmarked_recipes(self, user_id):
        best_bookmarked_recipes = Recipe.objects.annotate(
            bookmarks_count=Count("bookmark"),
        ).order_by("-bookmarks_count")[:1]

        # 각 레시피에 대해 사용자의 북마크 상태를 설정
        for recipe in best_bookmarked_recipes:
            recipe.bookmark_status = self.get_user_bookmark_status(recipe.id, user_id)

        return best_bookmarked_recipes

    # 특정 카테고리에 속하는 레시피를 가져오는 메서드
    def get_category_recipes(self, user_id, category_id):
        category_recipes = Recipe.objects.filter(category=category_id).annotate(
            likes_count=Count("like", distinct=True),
            bookmarks_count=Count("bookmark", distinct=True),
        )[:4]

        # 각 레시피에 대해 사용자의 좋아요 및 북마크 상태를 설정
        for recipe in category_recipes:
            recipe.like_status = self.get_user_like_status(recipe.id, user_id)
            recipe.bookmark_status = self.get_user_bookmark_status(recipe.id, user_id)

        return category_recipes

    # 메인 GET 메서드
    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 사용자 정보
        try:
            user = User.objects.get(id=user.id)
        except User.DoesNotExist:
            return Response({
                "status": 404,
                "message": "사용자를 찾을 수 없습니다.",
                "data": {}
            }, status=404)

        # 사용자의 상세 정보 상태
        detail_status = self.get_user_detail_status(user)

        # 각 카테고리 및 조건에 맞는 레시피를 가져와서 시리얼라이즈
        best_recipes = self.get_best_recipes(user.id)
        best_serializer = RecipeSerializer(best_recipes, many=True)

        best_bookmarked_recipes = self.get_best_bookmarked_recipes(user.id)
        best_bookmarked_serializer = RecipeSerializer(best_bookmarked_recipes, many=True)

        daily_recipes = self.get_category_recipes(user.id, category_id=1)
        daily_serializer = RecipeSerializer(daily_recipes, many=True)

        healthy_recipes = self.get_category_recipes(user.id, category_id=2)
        healthy_serializer = RecipeSerializer(healthy_recipes, many=True)

        desert_recipes = self.get_category_recipes(user.id, category_id=3)
        desert_serializer = RecipeSerializer(desert_recipes, many=True)

        midnight_snack_recipes = self.get_category_recipes(user.id, category_id=4)
        midnight_snack_serializer = RecipeSerializer(midnight_snack_recipes, many=True)

        # 최종적으로 Response 객체를 반환하여 데이터를 응답
        return Response({
            "status": 200,
            "message": "조회 성공",
            "data": {
                "detailStatus": detail_status,
                "best": best_serializer.data,
                "bestBookmarked": best_bookmarked_serializer.data,
                "daily": daily_serializer.data,
                "healthy": healthy_serializer.data,
                "desert": desert_serializer.data,
                "midnightSnack": midnight_snack_serializer.data,
            }
        })