from rest_framework.views import APIView
from rest_framework.response import Response
from recipes.models import Recipe
from .serializers import RecipeSerializer
from bookmarks.models import Bookmark
from likes.models import Like
from django.db.models import Count
from users.models import User
from rest_framework import status

from datetime import timedelta, datetime


class MainPageView(APIView):
    # 사용자가 특정 레시피를 좋아하는지 확인하여 -1 또는 1을 반환하는 메서드
    def get_user_like_status(self, recipe_id, user_id):
        like_status = Like.objects.filter(recipe_id=recipe_id, user_id=user_id).exists()
        return 1 if like_status else -1

    # 사용자가 특정 레시피를 북마크했는지 확인하여 -1 또는 1을 반환하는 메서드
    def get_user_bookmark_status(self, recipe_id, user_id):
        bookmark_status = Bookmark.objects.filter(
            recipe_id=recipe_id, user_id=user_id
        ).exists()
        return 1 if bookmark_status else -1

    # 사용자의 성별(gender)과 나이(age) 정보가 있는지 확인하여 상세 정보 상태를 반환하는 메서드
    def get_user_detail_status(self, user):
        return 1 if user.gender is not None and user.age is not None else -1

    def get_last_week_datetime(self):
        # 현재 날짜 계산
        today = datetime.today()
        # 이번 주 시작일 계산 (일요일 기준)
        # 파이썬은 월요일을 0으로 계산하기 때문에 일요일부터 계산하기 위해 1일을 추가로 빼줌
        start_of_this_week = today - timedelta(days=today.weekday()) - timedelta(days=1)
        # 저번 주 시작일 계산
        start_of_last_week = (start_of_this_week - timedelta(days=7)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # 저번 주 종료일 계산
        end_of_last_week = (start_of_this_week - timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        return start_of_last_week, end_of_last_week

    # 좋아요 수가 가장 많은 레시피를 가져오는 메서드
    def get_best_recipe(self, user_id):
        best_recipe = (
            Recipe.objects.filter(
                like__created_at__range=[*self.get_last_week_datetime()]
            )
            .annotate(
                likes_count=Count("like"),
            )
            .order_by("-likes_count")
            .first()
        )
        print(Recipe.objects.filter(
                like__created_at__range=[*self.get_last_week_datetime()]
            )
            .annotate(
                likes_count=Count("like"),
            )
            .order_by("-likes_count").query)
        # 각 레시피에 대해 사용자의 좋아요 상태를 설정
        best_recipe.like_status = self.get_user_like_status(best_recipe.id, user_id)

        best_recipe.likes_count = len(Like.objects.filter(recipe=best_recipe))
        return best_recipe

    # 북마크된 레시피 중 가장 인기 있는 레시피를 가져오는 메서드
    def get_best_bookmarked_recipe(self, user_id):
        best_bookmarked_recipe = (
            Recipe.objects.filter(
                bookmark__created_at__range=[*self.get_last_week_datetime()]
            )
            .annotate(
                bookmarks_count=Count("bookmark"),
            )
            .order_by("-bookmarks_count")
            .first()
        )

        # 각 레시피에 대해 사용자의 북마크 상태를 설정
        best_bookmarked_recipe.bookmark_status = self.get_user_bookmark_status(
            best_bookmarked_recipe.id, user_id
        )

        best_bookmarked_recipe.bookmarks_count = len(Bookmark.objects.filter(recipe=best_bookmarked_recipe))

        return best_bookmarked_recipe

    # 특정 카테고리에 속하는 레시피를 가져오는 메서드
    def get_category_recipes(self, user_id, category_id):
        category_recipes = (
            Recipe.objects.filter(category=category_id)
            .annotate(
                likes_count=Count("like", distinct=True),
                bookmarks_count=Count("bookmark", distinct=True),
            )
            .order_by("-id")[:4]
        )

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
            return Response(
                {"status": 404, "message": "사용자를 찾을 수 없습니다.", "data": {}},
                status=404,
            )

        # 사용자의 상세 정보 상태
        detail_status = self.get_user_detail_status(user)

        # 각 카테고리 및 조건에 맞는 레시피를 가져와서 시리얼라이즈
        best_recipe = self.get_best_recipe(user.id)
        best_serializer = RecipeSerializer(best_recipe)

        best_bookmarked_recipe = self.get_best_bookmarked_recipe(user.id)
        best_bookmarked_serializer = RecipeSerializer(best_bookmarked_recipe)

        daily_recipes = self.get_category_recipes(user.id, category_id=1)
        daily_serializer = RecipeSerializer(daily_recipes, many=True)

        healthy_recipes = self.get_category_recipes(user.id, category_id=2)
        healthy_serializer = RecipeSerializer(healthy_recipes, many=True)

        desert_recipes = self.get_category_recipes(user.id, category_id=3)
        desert_serializer = RecipeSerializer(desert_recipes, many=True)

        midnight_snack_recipes = self.get_category_recipes(user.id, category_id=4)
        midnight_snack_serializer = RecipeSerializer(midnight_snack_recipes, many=True)

        # 최종적으로 Response 객체를 반환하여 데이터를 응답
        return Response(
            {
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
                },
            }
        )
