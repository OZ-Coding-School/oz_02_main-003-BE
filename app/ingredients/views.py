from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from .models import Ingredient
from likes.models import Like
from bookmarks.models import Bookmark

class IngredientTypeView(APIView):
    def get(self, request, type):
        # type이 'recipe'인지 'fridge'인지 확인
        if type == 'recipe':
            # 레시피에 사용되는 재료 조회
            ingredients = Ingredient.objects.filter(recipe_ingredient__isnull=False).distinct()
        elif type == 'fridge':
            # 사용자의 냉장고에 저장된 재료 조회
            user_id = 1 # 토큰에서 사용자 ID 추출
            ingredients = Ingredient.objects.filter(fridge__user_id=user_id).distinct()
            print(ingredients)
        else:
            # 잘못된 type이 입력된 경우
            return Response({"status": 400, "message": "잘못된 type입니다."}, status=400)

        # 재료 정보를 dictionary 형태로 변환
        ingredient_data = [
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "image": ingredient.image
            }
            for ingredient in ingredients
        ]

        # 응답 데이터 구성
        response_data = {
            "status": 200,
            "message": "조회 성공",
            "data": ingredient_data
        }

        # 응답 반환
        return Response(response_data)
    
class IngredientTypeSearchView(APIView):
    def get(self, request, type, search):
        if type == 'recipe':
            # 레시피에 사용되는 재료 검색
            ingredients = Ingredient.objects.filter(name__icontains=search, recipe_ingredient__isnull=False).distinct()
        elif type == 'fridge':
            # 사용자의 냉장고에 저장된 재료 검색
            user_id = request.user.id
            ingredients = Ingredient.objects.filter(name__icontains=search, fridge__user_id=user_id).distinct()
        else:
            return Response({"status": 400, "message": "잘못된 type입니다."}, status=400)

        ingredient_data = [
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "image": ingredient.image or ""  # image 필드가 None인 경우 빈 문자열로 처리
            }
            for ingredient in ingredients
        ]

        response_data = {
            "status": 200,
            "message": "조회 성공",
            "data": ingredient_data
        }

        return Response(response_data)