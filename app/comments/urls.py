from django.urls import path
from .views import CommentView

urlpatterns = [
    # /api/v1/comments
    path("", CommentView.as_view(), name="comment-view")
]