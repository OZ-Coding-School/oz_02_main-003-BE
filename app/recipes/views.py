from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView


class RecipeRecommendView(APIView):

    def post(self, request):
        data = request.data
        return Response(data)


class CreateRecipe(APIView):

    def post(self, request):
        data = request.data
        return Response(data)

    def put(self, request):
        data = request.data
        return Response(data)


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

