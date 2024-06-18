from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .utils.save_similary import save_all_recipe_similarities




class SaveRecipeSimilarView(APIView):
    def get(self, request):
        # 모든 레시피 간 유사도 계산 및 저장
        save_all_recipe_similarities()

        return Response({"message": "Recipe similarities saved successfully."})

