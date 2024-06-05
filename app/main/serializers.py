# serializers.py
from rest_framework import serializers
from recipes.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    bookmarks_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['user', 'title', 'main_image', 'likes_count', 'bookmarks_count']

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_bookmarks_count(self, obj):
        return obj.bookmark_set.count()
