from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recipe
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

