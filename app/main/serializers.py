# serializers.py
from recipes.models import Recipe
from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'id']

class RecipeSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    bookmarks_count = serializers.IntegerField(read_only=True)
    like_status = serializers.IntegerField(read_only=True)
    recipe_id = serializers.IntegerField(source='id', read_only=True)
    bookmark_status = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    
    
    class Meta:
        model = Recipe
        fields = ['recipe_id', 'user', 'title', 'main_image', 'likes_count', 'bookmarks_count', 'like_status', 'bookmark_status']

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_bookmarks_count(self, obj):
        return obj.bookmark_set.count()
