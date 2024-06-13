from django.core.exceptions import ValidationError
from django.shortcuts import redirect

import urllib.parse, urllib.request

import json
from common.data.envdata import *
from common.utils.token_handler import TokenManager
from users.utils import (
    get_or_create_social_user,
    update_or_create_refresh_token_data,
)


class SocialLoginServices:
    """
    소셜 로그인 화면으로 리다이렉트 하기 위한 서비스

    ---
    """

    @classmethod
    def get_social_login_redirect_object(cls, type, dev):
        app_key = OAUTH2_CLIENT_ID[type]
        OAUTH2_API = {
            "kakao": "https://kauth.kakao.com/oauth/authorize",
            "google": "https://accounts.google.com/o/oauth2/v2/auth",
        }
        callback_uri = f"{HOST}/api/v1/users/auth/login/callback/{type}/{dev if dev else 0}"
        redirect_uri = f"{OAUTH2_API[type]}?client_id={app_key}&response_type=code&redirect_uri={callback_uri}"
        if type == "google":
            scope = (
                "https://www.googleapis.com/auth/userinfo.email "
                + "https://www.googleapis.com/auth/userinfo.profile"
            )
            redirect_uri = f"{redirect_uri}&scope={scope}"

        response = redirect(redirect_uri)
        return response


class SocialLoginCallbackServices:
    """
    소셜 로그인 콜백 서비스

    ---
    """

    CALLBACK_URI = f"{HOST}/api/v1/users/auth/login/callback"

    def __init__(self, type, dev):
        self.type = type
        self.dev = dev

    def get_social_token(self, code):
        """
        각 소셜의 액세스 토큰 받기

        ---
        """

        TOKEN_API = {
            "kakao": "https://kauth.kakao.com/oauth/token",
            "google": "https://oauth2.googleapis.com/token",
        }

        params = {
            "grant_type": "authorization_code",
            "client_id": OAUTH2_CLIENT_ID[self.type],
            "redirect_uri": f"{self.CALLBACK_URI}/{self.type}/{self.dev}",
            "client_secret": OAUTH2_CLIENT_SECRET[self.type],
            "code": code,
        }

        token_api = TOKEN_API[self.type]
        url = f"{token_api}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(url, method="POST")

        try:
            with urllib.request.urlopen(request) as response:
                if response.status != 200:
                    raise ValidationError(f"{type}_token is invalid")

                token_response = json.loads(response.read().decode())
                access_token = token_response.get("access_token")

                return access_token
        except urllib.error.URLError as e:
            raise ValidationError(
                f"Failed to obtain access token from ${type}: {e.reason}"
            )

    def get_user(self, social_token):
        USER_INFO_API = {
            "kakao": "https://kapi.kakao.com/v2/user/me",
            "google": "https://www.googleapis.com/oauth2/v3/userinfo",
        }

        params = {"access_token": social_token}
        url = f"{USER_INFO_API[self.type]}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(url)

        try:
            with urllib.request.urlopen(request) as response:
                if response.status != 200:
                    raise ValidationError(f"Failed to obtain user info from {type}.")

                user_info = json.loads(response.read().decode())
                user = get_or_create_social_user(
                    type=self.type,
                    id=self.get_user_data(user_info, "id"),
                    image_url=self.get_user_data(user_info, "image"),
                )

                return user
        except urllib.error.URLError as e:
            raise ValidationError(f"Failed to obtain user info from {type}: {e.reason}")

    def get_user_data(self, user_info, target):
        """
        각 사이트의 정보를 키값을 통해 가져오기

        ---
        user_info: 가져올 데이터가 담겨진 객체
        target: 가져올 데이터
        """
        USER_INFO_KEYS = {
            "kakao": {
                "id": ("id",),
                "image": ("properties", "thumbnail_image"),
            },
            "google": {"id": ("sub",), "image": ("picture",)},
        }

        data = user_info
        for key in USER_INFO_KEYS[self.type][target]:
            data = data[key]
        return data

    def get_access_token(self, user):
        """
        user를 통해 Refresh Token을 생성 및 DB에 저장하고 Access Token 반환

        ___
        """

        # Refresh Token 생성
        claims = {"is_staff": user.is_staff, "social_id": user.social_id}
        refresh_token = TokenManager.create_refresh_token_with_claims(user, claims)

        # DB에 토큰 저장
        update_or_create_refresh_token_data(user, refresh_token)

        # 생성된 Refresh Token으로 Access Token 반환
        return str(refresh_token.access_token)
