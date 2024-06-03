from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recipe, Recipe_ingredient, Recipe_step
from .serializers import RecipeSerializer
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
        return Response({"레시피 조회": id})

    def delete(self, request, id):
        return Response({"레시피 삭제": id})


class RecipeCategoryListView(APIView):

    def get(self, request, category):
        return Response({"레시피 조회": category})
    
class RecipeSearchKeywordView(APIView):

    def get(self, request, keyword):
        return Response({"레시피 조회": keyword})

