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
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data
        recipe_id = data.get("recipe")
        comment_text = data.get("comment")

        try:
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
                "recipe_id": recipe_id,
                "comment": comment_text,
            },
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data

        comment_id = data.get("id")
        recipe_id = data.get("recipe")
        comment_text = data.get("comment")

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        if comment.user != user:
            return Response(
                {"error": "You are not authorized to update this comment."},
                status=status.HTTP_403_FORBIDDEN,
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
                "recipe_id": recipe_id,
                "comment": comment_text,
            },
            status=status.HTTP_200_OK,
        )


class CommentDeleteView(APIView):
    def delete(self, request, comment_id):
        
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # 주어진 comment_id로 댓글 조회
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            # 주어진 comment_id에 해당하는 댓글이 없는 경우
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # 사용자가 관리자(is_staff=True)인지 또는 댓글 작성자인지 확인
        if not (user.is_staff or comment.user.id == user.id):
            # 사용자가 관리자가 아니면 권한 거부 메시지 반환
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        # 관리자이거나 댓글 작성자인 경우 댓글 삭제
        comment.delete()
        # 삭제 완료 메시지와 함께 204 No Content 반환
        return Response(
            {"status": 200, "message": "댓글 삭제 성공"}, status=status.HTTP_200_OK
        )