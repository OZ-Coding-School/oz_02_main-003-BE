from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Bookmark
from recipes.models import Recipe
from users.models import User


class BookmarkToggleView(APIView):
    def post(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        recipe_id = request.data.get("recipe")
        status_value = request.data.get("status")

        if status_value not in ["1", "-1"]:
            return Response(
                {"status": 400, "message": "잘못된 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        status_value = int(status_value)

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {"status": 404, "message": "레시피를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if status_value == 1:  # 등록
            Bookmark.objects.get_or_create(user=user, recipe=recipe)
            message = "즐겨찾기 등록"
        elif status_value == -1:  # 취소
            Bookmark.objects.filter(user=user, recipe=recipe).delete()
            message = "즐겨찾기 취소"

        return Response(
            {"status": 201, "message": message, "data": {"status": status_value}},
            status=status.HTTP_201_CREATED,
        )
