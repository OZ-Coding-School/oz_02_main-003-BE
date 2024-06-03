from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from common.data.envdata import GOOGLE_OAUTH2_CLIENT_ID, KAKAO_OAUTH2_CLIENT_ID
from django.contrib.auth import get_user_model
from django.utils import timezone

from .services import (
    kakao_get_access_token,
    kakao_get_user_info,
    google_get_access_token,
    google_get_user_info,
)

User = get_user_model()

from users.utils import get_or_create_social_user, TokenCreator
from users.models import User_refresh_token


class KakaoLoginView(APIView):
    def get(self, request):
        client_id = KAKAO_OAUTH2_CLIENT_ID
        redirect_uri = "http://127.0.0.1:8000/api/v1/users/auth/kakao/callback"
        kakao_auth_api = "https://kauth.kakao.com/oauth/authorize"
        response = redirect(
            f"{kakao_auth_api}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        )
        return response


class KakaoLoginCallbackView(APIView):
    def get(self, request):
        data = request.query_params.copy()

        # access_token 발급 요청
        code = data.get("code")
        if not code:
            return Response(status=400)

        access_token = kakao_get_access_token(code)
        user_info = kakao_get_user_info(access_token=access_token)
        user = get_or_create_social_user(
            type="kakao",
            id=user_info["id"],
            image=user_info["properties"]["thumbnail_image"],
        )
        refresh_token = TokenCreator.create_token_by_data(
            user_id=user.id,
            claims={"is_staff": user.is_staff, "social_id": user.social_id},
        )
        refresh_token_data = {
            "user": user,
            "token": str(refresh_token),
            "estimate": timezone.now() + refresh_token.lifetime,
        }
        User_refresh_token.objects.update_or_create(
            defaults=refresh_token_data, **{"user": user}
        )

        response = Response({"status": 200, "message": "로그인 성공"})
        response.set_cookie("access", str(refresh_token.access_token), httponly=True)

        user.last_login = timezone.now()
        user.save()

        return response


class GoogleLoginView(APIView):
    def get(self, requests):
        app_key = GOOGLE_OAUTH2_CLIENT_ID
        scope = (
            "https://www.googleapis.com/auth/userinfo.email "
            + "https://www.googleapis.com/auth/userinfo.profile"
        )
        redirect_uri = "http://127.0.0.1:8000/api/v1/users/auth/google/callback"
        google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth"
        response = redirect(
            f"{google_auth_api}?client_id={app_key}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
        )
        return response


class GoogleLoginCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        google_token_api = "https://oauth2.googleapis.com/token"

        access_token = google_get_access_token(google_token_api, code)
        user_data = google_get_user_info(access_token=access_token)

        """
        "sub": "114379102616868503357",
        114379102616868503357
        "name": "윤준명",
        "givenName": "준명",
        "familyName": "윤",
        "picture": "https://lh3.googleusercontent.com/a/ACg8ocJ3W3XHC9ts4R8Lo7PNNLQDeji-hp6trLn39ic2shznfcpGxw=s96-c",
        "email": "wnsaud2233@gmail.com",
        "emailVerified": true,
        "locale": "ko"
        """

        profile_data = {
            "username": user_data["email"],
            "first_name": user_data.get("given_name", ""),
            "last_name": user_data.get("family_name", ""),
            "nickname": user_data.get("nickname", ""),
            "name": user_data.get("name", ""),
            "image": user_data.get("picture", None),
            "social": "google",
        }
        # user, _ = social_user_get_or_create(**profile_data)

        # response = redirect('https://naver.com')
        # response = jwt_login(response=response, user=user)

        # return response
        return Response(user_data)


class LoginView(APIView):
    def post(self, request):
        return Response("Login 완료")


class LogoutView(APIView):
    def post(self, request):
        return Response("유저 토큰 삭제")


class UserView(APIView):
    def delete(self, request):
        return Response("계정 삭제 완료")


class UpdateNicknameView(APIView):
    def put(self, request):
        return Response("닉네임 변경 완료")


class UpdateImageView(APIView):
    def put(self, request):
        return Response("프로필 사진 변경 완료")


class MyPageView(APIView):
    def get(self, request, user_id, scroll_count):
        return Response({"user_id": user_id, "scroll_count": scroll_count})


class AlertEnableSettingView(APIView):
    def put(self, request):
        return Response("알림 설정 완료")
