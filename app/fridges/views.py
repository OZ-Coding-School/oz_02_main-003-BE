from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Fridge, Ingredient

User = get_user_model()


class FridgeView(APIView):
    def get(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        fridge_items = Fridge.objects.filter(user=user)
        ingredients = [
            {"id": item.ingredient.id, "name": item.ingredient.name}
            for item in fridge_items
        ]

        return Response(
            {
                "status": 200,
                "message": "조회 성공",
                "data": {
                    "nickname": user.nickname,  # assuming `nickname` is a field in the custom User model
                    "ingredients": ingredients,
                },
            },
            status=status.HTTP_200_OK,
        )


class FridgeIngredientAddView(APIView):

    def post(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data

        for item in data:
            ingredient_id = item.get("id")
            ingredient_status = item.get("status")

            if ingredient_id is None or ingredient_status is None:
                return Response(
                    {"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST
                )

            ingredient = get_object_or_404(Ingredient, pk=ingredient_id)

            if ingredient_status == 1:
                # 재료 추가
                Fridge.objects.get_or_create(user=user, ingredient=ingredient)
            elif ingredient_status == 0:
                # 재료 삭제
                Fridge.objects.filter(user=user, ingredient=ingredient).delete()
            else:
                return Response(
                    {"error": "Invalid status value"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"status": 201, "message": "재료 추가, 삭제 성공"},
            status=status.HTTP_201_CREATED,
        )
