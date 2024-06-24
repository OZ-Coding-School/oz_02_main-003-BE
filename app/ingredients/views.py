from django.shortcuts import render
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Ingredient
from recipes.models import Recipe_ingredient


def get_ingredients_in_recipes():
    recipe_ingredient_ids = Recipe_ingredient.objects.values_list(
        "ingredient_id", flat=True
    ).distinct()

    return Ingredient.objects.filter(id__in=recipe_ingredient_ids)


def get_ingredients_by_type(type):
    if type == "recipe":
        # 레시피에 사용되는 재료 조회
        return Ingredient.objects.all()
    elif type == "fridge":
        return get_ingredients_in_recipes()


class IngredientTypeView(APIView):
    def get(self, request, type):
        user_id = request.user.id
        if not user_id:
            return Response(
                {"status": 400, "message": "사용자 인증이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if type not in ["recipe", "fridge"]:
            # 잘못된 type이 입력된 경우
            return Response(
                {"status": 400, "message": "잘못된 type입니다."}, status=400
            )

        ingredients = get_ingredients_by_type(type)

        # 재료 정보를 dictionary 형태로 변환
        ingredient_data = [
            {
                "id": ingredient.id,
                "name": ingredient.name,
            }
            for ingredient in ingredients
        ]

        # 응답 데이터 구성
        response_data = {"status": 200, "message": "조회 성공", "data": ingredient_data}

        # 응답 반환
        return Response(response_data)


class IngredientTypeSearchView(APIView):
    def get(self, request, type, search):
        user_id = request.user.id
        if not user_id:
            return Response(
                {"status": 400, "message": "사용자 인증이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if type not in ["recipe", "fridge"]:
            # 잘못된 type이 입력된 경우
            return Response(
                {"status": 400, "message": "잘못된 type입니다."}, status=400
            )

        ingredients = get_ingredients_by_type(type).filter(name__icontains=search)

        ingredient_data = [
            {
                "id": ingredient.id,
                "name": ingredient.name,
            }
            for ingredient in ingredients
        ]

        response_data = {"status": 200, "message": "조회 성공", "data": ingredient_data}

        return Response(response_data)
