from django.urls import path
from .views import CommentView, CommentDeleteView

urlpatterns = [
    # /api/v1/comments
    path("", CommentView.as_view(), name="comment-view"),
    # /api/v1/comments/1
    path("/<int:comment_id>", CommentDeleteView.as_view(), name="comment-delete-view"),
]
