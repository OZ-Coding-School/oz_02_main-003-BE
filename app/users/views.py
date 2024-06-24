from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import redirect
from rest_framework import status
from django.http import JsonResponse

from .services import SocialLoginServices, SocialLoginCallbackServices

from users.models import User_refresh_token

User = get_user_model()

from users.customs.authentication import CustomCookieAuthentication
from common.data.envdata import ACCESS_TOKEN_COOKIE_NAME

from rest_framework.permissions import IsAuthenticated
from .serializers import UserDetailSerializer, UserNicknameSerializer
from .serializers import UserProfileSerializer, RecipeSerializer
from recipes.models import Recipe
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404

from datetime import timedelta


class LoginView(APIView):
    authentication_classes = []

    def get(self, request):
        social_types = ("kakao", "google")

        # 소셜로그인인지 확인
        social_type = request.GET.get("social", None)

        if social_type is not None and social_type not in social_types:
            return Response({"status": 400, "message": "잘못된 소셜 타입"}, status=400)
        if social_type in social_types:
            dev = request.GET.get("dev", 0)
            return SocialLoginServices.get_social_login_redirect_object(
                social_type, dev
            )

        # 소셜 로그인이 아니라면 토큰 로그인 진행
        authenticator = CustomCookieAuthentication()
        user, token = authenticator.authenticate(request)
        if user:
            return Response({"status": 200, "message": "로그인 성공"})
        return Response({"status": 400, "message": "토큰이 없습니다."})


class LoginCallbackView(APIView):
    authentication_classes = []

    def get(self, request, social, dev):

        data = request.query_params.copy()

        code = data.get("code")
        if not code:
            return Response(status=400)

        slcs = SocialLoginCallbackServices(social, dev)

        # social_token 발급 요청
        social_token = slcs.get_social_token(code)
        # social_token 을 통해 user 객체 가져오기(or 생성)
        user = slcs.get_user(social_token)
        # 가져온 user 객체를 통해 access_token 생성
        access_token = slcs.get_access_token(user)
        # return Response(get_cookie_settings(request, access_token, dev))
        redirect_uri = ["https://ndd.life", "http://localhost:5173"]
        response = redirect(redirect_uri[dev])
        host = request.META.get("HTTP_HOST")
        if host and (host.find("localhost") or host.find("127.0.0.1")):
            domain = None  # localhost나 127.0.0.1인 경우 domain을 생략
        else:
            domain = ".ndd.life"  # 실제 도메인 설정
        response.set_cookie(
            key="ndd_access",
            max_age=timedelta(days=30),
            value=access_token,
            httponly=True,
            domain=domain,
        )

        user.last_login = timezone.now()
        user.is_login = True
        user.save()

        return response


class LogoutView(APIView):
    authentication_classes = [CustomCookieAuthentication]

    def post(self, request):
        user = request.user
        if not user:
            return Response({"status": "400", "message": "토큰이 없습니다"}, 400)

        refresh_token_obj = User_refresh_token.objects.get(user=user)
        refresh_token_obj.delete()

        user.is_login = False
        user.save()

        response = Response({"status": "200", "meesage": "로그아웃 성공"})
        response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME)

        return response


class UserView(APIView):
    def get(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 사용자의 레시피를 조회합니다.
        recipes = Recipe.objects.filter(user=user)
        recipe_data = []  # 레시피 데이터를 저장할 리스트

        for recipe in recipes:
            recipe_data.append(
                {"id": recipe.id, "title": recipe.title, "image": recipe.main_image.url}
            )

        serializer = UserSerializer(user)
        user_data = serializer.data

        user_data["recipe"] = recipe_data

        return Response(
            {"status": 200, "message": "조회 성공", "data": user_data},
            status=status.HTTP_200_OK,
        )


class UserDeleteView(APIView):
    def delete(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.delete()
        return Response(
            {"status": 200, "message": "삭제 성공"}, status=status.HTTP_200_OK
        )


class UpdateNicknameView(APIView):

    def put(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserNicknameSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response_data = {"status": 200, "message": "변경 성공"}
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import base64
import os
from django.core.files.base import ContentFile
from .utils import generate_image_path, upload_image
from config import settings
from botocore.exceptions import NoCredentialsError
from config.settings import MEDIA_URL


class UserImageView(APIView):
    def post(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        image_data = request.data.get("image")
        if image_data == "":
            user.image = ""
            user.save()

            return JsonResponse(
                {
                    "status": 200,
                    "message": "이미지 데이터가 빈 문자열입니다.",
                    "image_url": "",
                },
                status=status.HTTP_200_OK,
            )

        if not image_data:
            return JsonResponse(
                {"status": 400, "message": "이미지 데이터가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]

            # settings에서 BUCKET_PATH를 불러와서 경로 조합
            image_path, relative_image_path = generate_image_path(user, ext)

            # 파일 저장
            content = base64.b64decode(imgstr)
            content_file = ContentFile(content)

            if upload_image(content_file, image_path):
                user.image = relative_image_path
                user.save()

                return JsonResponse(
                    {
                        "status": 200,
                        "message": "프로필 사진 저장 완료",
                        "image_url": get_image_uri(relative_image_path),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return JsonResponse(
                    {"status": 500, "message": "AWS 자격 증명이 잘못되었습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            return JsonResponse(
                {
                    "status": 500,
                    "message": f"프로필 사진 저장 중 오류가 발생했습니다: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


from common.utils.image_utils import get_image_uri


class MyPageView(APIView):
    def get(self, request, id, cnt):
        cnt = int(cnt)
        user = request.user

        # 로그인된 사용자인지 확인
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 선택한 유저 ID가 0인 경우 현재 로그인된 사용자 정보를 사용
        if id == 0:
            target_user = user
        else:
            target_user = get_object_or_404(User, pk=id)

        try:
            total_recipes_count = Recipe.objects.filter(user=target_user).count()
            # 유저의 레시피를 필터링하고 페이징 처리
            recipes = Recipe.objects.filter(user=target_user).order_by("-id")[
                cnt * 15 : (cnt + 1) * 15
            ]

            # cnt에 관계없이 레시피 직렬화
            recipe_serializer = RecipeSerializer(recipes, many=True)

            if cnt == 0:
                user_serializer = UserProfileSerializer(target_user)
                response_data = {
                    "status": 200,
                    "message": "마이페이지 조회 완료",
                    "data": {
                        "image": get_image_uri(user_serializer.data["image"]),
                        "total_recipes_count": total_recipes_count,
                        "nickname": user_serializer.data["nickname"],
                        "recipes": recipe_serializer.data,
                    },
                }
            else:
                response_data = {
                    "status": 200,
                    "message": "마이페이지 조회 완료",
                    "data": {"recipes": recipe_serializer.data},
                }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"status": 500, "message": "알 수 없는 오류", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AlertEnableView(APIView):
    def get(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 400, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        enable = User.objects.get(id=user.id).is_alert
        return Response(
            {"status": 200, "message": "알림여부 조회 성공", "data": {"status": enable}}
        )

    def put(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 400, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        enable = request.data.get("enable", False)

        user.is_alert = enable
        user.save()

        return Response(
            {"status": 200, "message": "알림 설정이 업데이트되었습니다."},
            status=status.HTTP_200_OK,
        )


class UserDetailView(APIView):
    def post(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserDetailSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response_data = {"status": 200, "message": "변경 성공"}
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
