from rest_framework import serializers
from .models import User
from recipes.models import Recipe

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['age', 'gender', 'is_alert']
        
class UserNicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname']
        
    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 존재하는 닉네임입니다.")
        return value
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'image']
        
class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id','main_image']

class UserProfileSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['nickname', 'image', 'recipes']