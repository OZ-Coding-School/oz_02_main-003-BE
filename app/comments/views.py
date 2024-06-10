from rest_framework.views import APIView
from rest_framework.response import Response
from comments.models import Comment
from users.models import User
from recipes.models import Recipe
from django.http import JsonResponse
from rest_framework import status


class CommentView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data

        user_id = data.get("user")
        recipe_id = data.get("recipe")
        comment_text = data.get("comment")

        try:
            user = User.objects.get(pk=user_id)
            recipe = Recipe.objects.get(pk=recipe_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
        comment = Comment.objects.create(user=user, recipe=recipe, comment=comment_text)
        return Response(
            {
                "comment_id": comment.id,
                "user_id": user_id,
                "recipe_id": recipe_id,
                "comment": comment_text,
            },
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        data = request.data

        comment_id = data.get("id")
        user_id = data.get("user")
        recipe_id = data.get("recipe")
        comment_text = data.get("comment")

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )

        comment.user = user
        comment.recipe = recipe
        comment.comment = comment_text
        comment.save()

        return Response(
            {
                "comment_id": comment.id,
                "user_id": user_id,
                "recipe_id": recipe_id,
                "comment": comment_text,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        # 요청에서 comment_id와 user_id 가져오기
        comment_id = request.data.get("comment_id")
        user_id = request.data.get("user_id")

        # comment_id가 제공되지 않은 경우
        if not comment_id:
            return Response(
                {"error": "comment_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        # user_id가 제공되지 않은 경우
        if not user_id:
            return Response(
                {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 주어진 user_id로 사용자 조회
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            # 주어진 user_id에 해당하는 사용자가 없는 경우,
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # 사용자가 관리자(is_staff=True)인지 확인
        if not user.is_staff:
            # 사용자가 관리자가 아니면 권한 거부 메시지 반환
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            # 주어진 comment_id로 댓글 조회
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            # 주어진 comment_id에 해당하는 댓글이 없는 경우,
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # 관리자 확인 후 댓글 삭제
        comment.delete()
        # 삭제 완료 메시지와 함께 204 No Content 반환
        return Response(
            {"message": "삭제 요청: 삭제완료"}, status=status.HTTP_204_NO_CONTENT
        )
