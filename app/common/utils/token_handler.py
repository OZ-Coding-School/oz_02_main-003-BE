from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


import jwt


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
    def get_user_id_from_access_token(cls, access_token):
        return jwt.decode(access_token, options={"verify_signature": False})["user_id"]
