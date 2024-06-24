from django.urls import path
from .views import BookmarkToggleView

urlpatterns = [
    # /api/v1/bookmarks
    path("", BookmarkToggleView.as_view(), name="bookmark-toggle"),
]