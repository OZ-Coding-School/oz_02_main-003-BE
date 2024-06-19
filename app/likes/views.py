from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Like
from recipes.models import Recipe
from users.models import User


class LikeToggleView(APIView):
    def post(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        recipe_id = request.data.get("recipe")
        
        try:
            print(Like.objects.get(user=user, recipe_id=recipe_id))
            Like.objects.get(user=user, recipe_id=recipe_id).delete()
            message = "좋아요 취소"
            status_value = -1
            
        except Recipe.DoesNotExist:
            return Response(
                {"status": 404, "message": "레시피를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        except Like.DoesNotExist:
            Like.objects.create(user=user, recipe_id=recipe_id)
            message = "좋아요 등록"
            status_value = 1
            
        return Response(
            {"status": 201, "message": message, "data": {"status": status_value}},
            status=status.HTTP_201_CREATED,
        )
