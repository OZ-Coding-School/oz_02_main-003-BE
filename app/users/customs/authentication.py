from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from common.data.envdata import ACCESS_TOKEN_COOKIE_NAME
from common.utils.token_handler import TokenManager
from rest_framework.response import Response

from ..models import User_refresh_token

from config import settings

User = get_user_model()

from common.exceptions import CustomException
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


class CustomCookieAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 쿠키에서 토큰 추출
        access_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE_NAME, None)

        # 토큰이 없을 경우 로그인 과정 진행
        if not access_token:
            return (None, None)
        
        try:
            # 서명 검증과 만료 검증을 포함하여 토큰 디코딩
            payload = TokenManager.get_token_payload(access_token)
            # 유효한 토큰이면 payload에서 user_id를 반환
            # return payload["user_id"]
            user = User.objects.get(id=payload["user_id"])
            access_token = TokenManager.get_new_access_token(user.id)
            return (user, access_token)
        except ExpiredSignatureError:
            # 토큰이 만료된 경우
            print("Token has expired")
            # 만료된 토큰의 payload를 검증 없이 디코딩
            # payload = jwt.decode(access_token, options={"verify_signature": False})
            payload = TokenManager.get_token_payload_without_sign(access_token)
        except InvalidTokenError:
            # 유효하지 않은 토큰
            print("Invalid token")
            raise CustomException("유효하지 않은 토큰", 401, -499)

        user_id = payload.get("user_id")
        try:
            user = User.objects.get(id=user_id)

            # 이미 로그아웃 한 유저라면
            if user.is_login is False:
                response = Response(
                    {"status": 401, "message": "다시 로그인 해주시기 바랍니다"},
                    status=401,
                )
                response.delete_cookie("ndd_access")
                raise CustomException("다시 로그인 해주시기 바랍니다", 403, -498)
            host = request.META.get("HTTP_HOST")
            if host and (host.find('localhost') or host.find('127.0.0.1')):
                domain = None  # localhost나 127.0.0.1인 경우 domain을 생략
            else:
                domain = '.ndd.life'  # 실제 도메인 설정
            # 에러 처리로 토큰 재발급 진행
            raise CustomException(f"토큰 재발급됨", 401, -401, data={"user_id": user_id, "domain": domain})
        except User.DoesNotExist:
            response = Response(
                {"status": 400, "message": "없는 유저 입니다."},
                status=400,
            )
            response.delete_cookie("ndd_access")
            return response
