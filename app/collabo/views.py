from django.shortcuts import render
from rest_framework.views import APIView
from .utils.interaction_utils import get_recent_interactions
from rest_framework.response import Response
from rest_framework import status

from .utils.save_similary import save_all_recipe_similarities


# class TestView(APIView):
#     def get(self, request):
#         try:
#             # 로그인한 사용자의 ID 가져오기
#             user_id = request.user.id

#             # 사용자의 최근 상호작용 레시피 ID 가져오기
#             recent_recipe_ids = get_recent_interactions(user_id)

#             # 유사한 레시피 추천
#             recommended_recipes = recommend_similar_recipes(user_id)

#             # 응답 데이터 생성
#             response_data = [
#                 {
#                     'id': recipe['id'],
#                     'title': recipe['title'],
#                     'description': recipe['description'],
#                     'main_image': recipe['main_image'],
#                     'ingredients': recipe['ingredients']
#                 }
#                 for recipe in recommended_recipes
#             ]

#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TestView(APIView):
    def get(self, request):
        # 모든 레시피 간 유사도 계산 및 저장
        save_all_recipe_similarities()

        return Response({"message": "Recipe similarities saved successfully."})

