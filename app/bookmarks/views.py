from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework import status
from .models import Bookmark
from recipes.models import Recipe
from users.models import User

class BookmarkToggleView(APIView):

    def post(self, request):
        user_id = request.data.get('user')
        recipe_id = request.data.get('recipe')
        status_value = int(request.data.get('status'))
        
        try:
            user = User.objects.get(id=user_id)
            recipe = Recipe.objects.get(id=recipe_id)
        except User.DoesNotExist:
            return Response({"status": 404, "message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Recipe.DoesNotExist:
            return Response({"status": 404, "message": "레시피를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 좋아요 상태에 따라 처리합니다.
        if status_value == 1:  # 등록
            Bookmark.objects.create(user=user, recipe=recipe)
            message = "즐겨찾기 등록"
        elif status_value == -1:  # 취소
            Bookmark.objects.filter(user=user, recipe=recipe).delete()
            message = "즐겨찾기 취소"
        else:
            return Response({"status": 400, "message": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"status": 201, "message": message, "data": {"status": status_value}}, status=status.HTTP_201_CREATED)