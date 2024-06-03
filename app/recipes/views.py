from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from .models import Recipe, Recipe_ingredient, Recipe_step
from .serializers import RecipeSerializer
from bookmarks.models import Bookmark
from likes.models import Like
from comments.models import Comment
from users.models import User

class RecipeRecommendView(APIView):

    def post(self, request):
        data = request.data
        return Response(data)


class CreateRecipe(APIView):
    def post(self, request):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            recipe = serializer.save()
            data = {
                "status": 201,
                "message": "레시피 작성 성공",
                "data": {
                    "id": recipe.id
                }
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, *args, **kwargs):
        recipe_id = request.data.get('id')
        recipe_ingredients_data = request.data.get('recipe_ingredients')
        recipe_steps_data = request.data.get('steps')

        # 필수 필드인 'id', 'ingredients', 'steps'를 확인
        if not recipe_id or recipe_ingredients_data is None or recipe_steps_data is None:
            return Response({"error": "레시피 ID, 재료 정보, 단계 정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response({"error": "해당 레시피를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecipeSerializer(recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                "status": 201,
                "message": "레시피 수정 성공",
                "data": {
                    "id": recipe.id
                }
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
            ingredients = Recipe_ingredient.objects.filter(recipe_id=id)
            steps = Recipe_step.objects.filter(recipe_id=id)
            # __ -> Comment 모델의 외래 키 User 모델의 id, nickname을 가져온다 
            # select_related -> 역참조 (User FK Comment)
            comments = Comment.objects.filter(recipe_id=id).select_related('user').values('id', 'user__id', 'user__nickname', 'updated_at', 'comment')
            serializer = RecipeSerializer(recipe)
            data = {
                "status": status.HTTP_200_OK,
                "message": "레시피 조회 성공",
                "data": {
                    # ** -> dict의 키-쌍 값을 개별적으로 펼쳐서 사용 가능
                    **serializer.data,
                    "bookmarks": bookmarks_count,
                    "likes": likes_count,
                    "user": {
                        "id": recipe.user.id,
                        "nickname": recipe.user.nickname,
                        "date": recipe.updated_at
                    },
                    "ingredients": [
                        {
                            "id": ingredient.id,
                            "name": ingredient.ingredient.name,
                            "quantity": ingredient.quantity,
                            "unit": ingredient.unit.unit
                        } for ingredient in ingredients
                    ],
                    "steps": [
                        {
                            "step": step.step,
                            "image": step.image
                        } for step in steps
                    ],
                    "comments": list(comments)
                }
            }
            return Response(data)
        except Recipe.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": f"ID {id}에 해당하는 레시피를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

    def get_object(self, id):
        try:
            return Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise NotFound(f"ID {id}에 해당하는 레시피를 찾을 수 없습니다.")

    def delete(self, request, id):
        recipe = self.get_object(id)
        recipe.delete()
        data = {
            "status": 200,
            "message": "레시피 삭제 성공"
        }
        return Response(data, status=status.HTTP_200_OK)

class RecipeCategoryListView(APIView):
    def get_category_name(self, category):
        category_mapping = {
            "daily": "일상요리",
            "healthy": "건강식",
            "midnight": "야식",
            "desert": "디저트",
        }
        return category_mapping.get(category, None)

    def get(self, request, category=None):
        user_id = 1  # 현재 사용자의 ID 가져오기
        category_name = self.get_category_name(category)
        
        if category == "like":
            # 사용자가 좋아요를 누른 레시피만 필터링
            recipes = Recipe.objects.filter(like__user_id=user_id)
        elif category == "book":
            # 사용자가 북마크한 레시피만 필터링
            recipes = Recipe.objects.filter(bookmark__user_id=user_id)
        elif category_name:
            # 특정 카테고리의 레시피만 필터링
            recipes = Recipe.objects.filter(category=category_name)
        else:
            # 모든 레시피 조회
            recipes = Recipe.objects.all()

        recipe_data = []
        for recipe in recipes:
            user = User.objects.get(id=recipe.user_id)
            like = Like.objects.filter(recipe_id=recipe.id, user_id=user_id).first()
            book = Bookmark.objects.filter(recipe_id=recipe.id, user_id=user_id).first()

            like_status = 1 if like else -1
            book_status = 1 if book else -1

            recipe_info = {
                "id": recipe.id,
                "user": user.name,
                "title": recipe.title,
                "image": recipe.image_1,
                "like": Like.objects.filter(recipe_id=recipe.id).count(),
                "like_status": like_status,
                "book": Bookmark.objects.filter(recipe_id=recipe.id).count(),
                "book_status": book_status
            }
            recipe_data.append(recipe_info)

        response_data = {
            "status": 200,
            "message": f"{category_name} 카테고리 레시피 조회 성공" if category_name else "레시피 조회 성공",
            "data": recipe_data
        }

        return Response(response_data)

class RecipeSearchKeywordView(APIView):
    def get(self, request, keyword):
        user_id = 1 
        if not keyword:
            return Response({"message": "검색어를 입력해 주세요."}, status=400)

        recipes = Recipe.objects.filter(
            Q(title__icontains=keyword) |
            Q(recipe_ingredient__ingredient__name__icontains=keyword) |
            Q(recipe_step__step__icontains=keyword)
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
                "user": user.name,
                "title": recipe.title,
                "image": recipe.image_1,
                "like": Like.objects.filter(recipe_id=recipe.id).count(),
                "like_status": like_status,
                "book": Bookmark.objects.filter(recipe_id=recipe.id).count(),
                "book_status": book_status
            }
            recipe_data.append(recipe_info)

        return Response(recipe_data)