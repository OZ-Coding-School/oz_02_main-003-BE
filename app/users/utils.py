from users.models import User

def get_or_create_social_user(type, id, image=None):
    social_id = f"{type}_{id}"
    data = {
        "social_type": type,
        "social_id": social_id,
        "image": image
    }
    user, _ = User.objects.get_or_create(**data)
    user.nickname = f"{user.id}번째 냉장고"
    user.save()
    return user

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user_id, claims):
        user = User.objects.get(id=user_id)
        token = super().get_token(user)

        for key, value in claims.items():
            token[key] = value
        return token

class TokenCreator:
    @classmethod
    def create_token_by_data(cls, user_id, claims):
        return CustomTokenObtainPairSerializer.get_token(user_id, claims)
    
    @classmethod
    def create_refresh_token_by_token(cls, old_refresh_token):
        return RefreshToken(old_refresh_token)