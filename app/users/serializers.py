from rest_framework import serializers
from .models import User

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