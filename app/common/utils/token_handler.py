from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from config import settings

import jwt

from django.contrib.auth import get_user_model

User = get_user_model()

from users.models import User_refresh_token
from common.exceptions import CustomException

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_refresh_token(cls, user, claims):
        token = super().get_token(user)

        for key, value in claims.items():
            token[key] = value
        return token


class TokenManager:
    @classmethod
    def create_refresh_token_with_claims(cls, user, claims):
        return CustomTokenObtainPairSerializer.get_refresh_token(user, claims)

    @classmethod
    def get_token_payload(cls, access_token):
        return jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])

    @classmethod
    def get_token_payload_without_sign(cls, access_token):
        return jwt.decode(access_token, options={"verify_signature": False})
    
    @classmethod
    def get_new_access_token(cls, user_id):
        user = User.objects.get(id=user_id)
        try:
            refresh_token = User_refresh_token.objects.get(user=user_id).token
            return RefreshToken(refresh_token).access_token
        except User_refresh_token.DoesNotExist:
            raise CustomException("Refresh Token이 없습니다. 다시 로그인해주세요", 400, -498)

