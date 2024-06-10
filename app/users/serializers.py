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
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'image']