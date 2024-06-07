from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from .models import Recipe, Recipe_ingredient, Recipe_step
from .serializers import RecipeSerializer
from ingredients.models import Ingredient
from bookmarks.models import Bookmark
from likes.models import Like
from comments.models import Comment
from users.models import User


class RecipeRecommendView(APIView):
    def post(self, request):
        # 요청에서 사용자가 입력한 재료 ID 목록 가져오기
        data = request.data
        ingredient_ids = data.get("ingredients", [])

        # 입력된 재료 ID로 실제 재료 객체 조회
        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        # 조회된 재료 객체의 이름 목록 생성
        ingredient_names = [ingredient.name for ingredient in ingredients]

        # 입력된 재료를 포함하는 레시피 목록 조회
        recipes = Recipe.objects.filter(
            recipe_ingredient__ingredient__in=ingredients
        ).distinct()

        # 사용자 ID 가져오기
        user_id = 1

        # 레시피 정보를 담을 리스트 초기화
        recipe_data = []
        for recipe in recipes:
            # 레시피 작성자 정보 가져오기
            user = User.objects.get(id=recipe.user_id)
            # 레시피 좋아요 수 가져오기
            like = Like.objects.filter(recipe_id=recipe.id).count()
            # 레시피 북마크 수 가져오기
            bookmark = Bookmark.objects.filter(recipe_id=recipe.id).count()

            # 사용자의 좋아요 및 북마크 상태 확인
            like_status = (
                Like.objects.filter(recipe_id=recipe.id, user_id=user_id)
                .values_list("id", flat=True)
                .first()
            )
            if like_status:
                like_status = 1
            else:
                like_status = -1

            bookmark_status = (
                Bookmark.objects.filter(recipe_id=recipe.id, user_id=user_id)
                .values_list("id", flat=True)
                .first()
            )
            if bookmark_status:
                bookmark_status = 1
            else:
                bookmark_status = -1

            # 레시피에 포함된 재료 이름 목록 생성
            recipe_ingredients = [
                item.ingredient.name for item in recipe.recipe_ingredient.all()
            ]

            # 입력된 재료 중 레시피에 포함된 재료와 포함되지 않은 재료 구분
            include_ingredients = [
                name for name in ingredient_names if name in recipe_ingredients
            ]
            not_include_ingredients = [
                name for name in recipe_ingredients if name not in include_ingredients
            ]

            recipe_info = {
                "nickname": user.nickname,
                "include_ingredients": include_ingredients,
                "not_include_ingredients": not_include_ingredients,
                "title": recipe.title,
                "likes": like,
                "bookmark": bookmark,
                "like_status": like_status,
                "bookmark_status": bookmark_status,
            }
            recipe_data.append(recipe_info)

        response_data = {
            "status": 200,
            "message": "조회 성공",
            "data": {"ingredients": ingredient_names, "recipes": recipe_data},
        }

        # 응답 반환
        return Response(response_data)


class CreateRecipe(APIView):
    def post(self, request):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            recipe = serializer.save()
            data = {
                "status": 201,
                "message": "레시피 작성 성공",
                "data": {"id": recipe.id},
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        recipe_id = request.data.get("id")
        recipe_ingredients_data = request.data.get("recipe_ingredients")
        recipe_steps_data = request.data.get("steps")

        # 필수 필드인 'id', 'ingredients', 'steps'를 확인
        if (
            not recipe_id
            or recipe_ingredients_data is None
            or recipe_steps_data is None
        ):
            return Response(
                {"error": "레시피 ID, 재료 정보, 단계 정보가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {"error": "해당 레시피를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RecipeSerializer(recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                "status": 201,
                "message": "레시피 수정 성공",
                "data": {"id": recipe.id},
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeDetailDeleteView(APIView):
    def get(self, request, id):
        try:
            recipe = Recipe.objects.get(pk=id)
            bookmarks_count = Bookmark.objects.filter(recipe_id=id).count()
            likes_count = Like.objects.filter(recipe_id=id).count()

            # 테스트용 user_id 하드코딩
            user_id = 1

            like_status = (
                Like.objects.filter(recipe_id=id, user_id=user_id)
                .values_list("id", flat=True)
                .first()
            )
            if like_status:
                like_status = 1
            else:
                like_status = -1

            bookmark_status = (
                Bookmark.objects.filter(recipe_id=id, user_id=user_id)
                .values_list("id", flat=True)
                .first()
            )
            if bookmark_status:
                bookmark_status = 1
            else:
                bookmark_status = -1

            # is_staff 값이 True이거나 user_id가 본인이면 canUpdate를 1로 설정
            user = User.objects.get(id=user_id)
            if user.is_staff or user.id == recipe.user.id:
                can_update = 1
            else:
                can_update = 0

            ingredients = Recipe_ingredient.objects.filter(recipe_id=id)
            steps = Recipe_step.objects.filter(recipe_id=id)
            comments = (
                Comment.objects.filter(recipe_id=id)
                .select_related("user")
                .values(
                    "id",
                    "user__id",
                    "user__nickname",
                    "updated_at",
                    "comment",
                    "user__image",
                )
            )

            # 각 댓글의 can_update 값 설정
            comment_data = []
            for comment in comments:
                if user.is_staff or comment["user__id"] == user_id:
                    comment_can_update = 1
                else:
                    comment_can_update = 0
                comment_data.append(
                    {
                        "id": comment["id"],
                        "user_id": comment["user__id"],
                        "user_nickname": comment["user__nickname"],
                        "profile_image": comment["user__image"],
                        "updated_at": comment["updated_at"],
                        "comment": comment["comment"],
                        "can_update": comment_can_update,
                    }
                )

            serializer = RecipeSerializer(recipe)
            data = {
                "status": status.HTTP_200_OK,
                "message": "레시피 조회 성공",
                "data": {
                    "can_update": can_update,
                    **serializer.data,
                    "like": likes_count,
                    "like_status": like_status,
                    "book": bookmarks_count,
                    "book_status": bookmark_status,
                    "user": {
                        "id": recipe.user.id,
                        "nickname": recipe.user.nickname,
                        "profile_image": recipe.user.image,
                        "date": recipe.updated_at,
                    },
                    "ingredients": [
                        {
                            "id": ingredient.id,
                            "name": ingredient.ingredient.name,
                            "quantity": ingredient.quantity,
                            "unit": ingredient.unit.unit,
                        }
                        for ingredient in ingredients
                    ],
                    "steps": [
                        {"step": step.step, "image": step.image} for step in steps
                    ],
                    "comments": comment_data,
                },
            }
            return Response(data)
        except Recipe.DoesNotExist:
            return Response(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": f"ID {id}에 해당하는 레시피를 찾을 수 없습니다.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def get_object(self, id):
        try:
            return Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise NotFound(f"ID {id}에 해당하는 레시피를 찾을 수 없습니다.")

    def delete(self, request, id):
        recipe = self.get_object(id)
        recipe.delete()
        data = {"status": 200, "message": "레시피 삭제 성공"}
        return Response(data, status=status.HTTP_200_OK)


class RecipeCategoryListView(APIView):

    def get_category_id(self, category_name):
        category_mapping = {
            "daily": 1,
            "healthy": 2,
            "desert": 3,
            "midnight_snack": 4,
            "none": 5,
        }
        return category_mapping.get(category_name, None)

    def get(self, request, category=None):
        user_id = 1  # 현재 사용자의 ID 가져오기

        if category in ["daily", "healthy", "desert", "midnight_snack", "none"]:
            category_id = self.get_category_id(category)
            recipes = Recipe.objects.filter(category=category_id).order_by('id')
        elif category == "like":
            recipes = Recipe.objects.filter(like__user_id=user_id).order_by('id')
        elif category == "book":
            recipes = Recipe.objects.filter(bookmark__user_id=user_id).order_by('id')
        else:
            recipes = Recipe.objects.all().order_by('id')

        recipe_data = []
        for recipe in recipes:
            user = User.objects.get(id=recipe.user_id)
            like = Like.objects.filter(recipe_id=recipe.id, user_id=user_id).first()
            book = Bookmark.objects.filter(recipe_id=recipe.id, user_id=user_id).first()

            like_status = 1 if like else -1
            book_status = 1 if book else -1

            recipe_info = {
                "id": recipe.id,
                "user": user.nickname,
                "title": recipe.title,
                "main_image": recipe.main_image,
                "like": Like.objects.filter(recipe_id=recipe.id).count(),
                "like_status": like_status,
                "book": Bookmark.objects.filter(recipe_id=recipe.id).count(),
                "book_status": book_status,
            }
            recipe_data.append(recipe_info)

        if category in ["daily", "healthy", "desert", "midnight_snack", "none"]:
            message = f"{category} 카테고리 레시피 조회 성공"
        else:
            message = "좋아요 및 북마크 레시피 조회 성공"

        response_data = {
            "status": 200,
            "message": message,
            "data": recipe_data,
        }

        return Response(response_data)

class RecipeSearchKeywordView(APIView):
    def get(self, request, keyword):
        user_id = 1
        if not keyword:
            return Response({"message": "검색어를 입력해 주세요."}, status=400)

        recipes = Recipe.objects.filter(
            Q(title__icontains=keyword)
            | Q(recipe_ingredient__ingredient__name__icontains=keyword)
            | Q(recipe_step__step__icontains=keyword)
        ).distinct()

        if not recipes:
            return Response({"message": "해당되는 레시피가 없습니다."}, status=404)

        recipe_data = []
        for recipe in recipes:
            user = User.objects.get(id=recipe.user_id)
            like = Like.objects.filter(recipe_id=recipe.id, user_id=user_id).first()
            book = Bookmark.objects.filter(recipe_id=recipe.id, user_id=user_id).first()

            like_status = 1 if like else -1
            book_status = 1 if book else -1

            recipe_info = {
                "id": recipe.id,
                "user": user.nickname,
                "title": recipe.title,
                "main_image": recipe.main_image,
                "like": Like.objects.filter(recipe_id=recipe.id).count(),
                "like_status": like_status,
                "book": Bookmark.objects.filter(recipe_id=recipe.id).count(),
                "book_status": book_status,
            }
            recipe_data.append(recipe_info)

        response_data = {
            "status": 200,
            "message": "레시피 조회 성공",
            "data": recipe_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
