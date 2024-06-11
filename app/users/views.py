from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import redirect
from rest_framework import status

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
    # authentication_classes = [CustomCookieAuthentication]
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

        response = Response({"status": 200, "message": "로그인 성공"})
        redirect_uri = ["https://ndd.life", "http://localhost:5173"]
        response = redirect(redirect_uri[dev])
        response.set_cookie(
            key="ndd_access",
            max_age=timedelta(days=30),
            value=access_token,
            httponly=True,
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
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    # "image": recipe.main_image
                }
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


class UpdateImageView(APIView):
    def put(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response("프로필 사진 변경 완료")


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
            # 유저의 레시피를 필터링하고 페이징 처리
            recipes = Recipe.objects.filter(user=target_user).order_by('id')[cnt * 15:(cnt + 1) * 15]

            # cnt에 관계없이 레시피 직렬화
            recipe_serializer = RecipeSerializer(recipes, many=True)

            if cnt == 0:
                user_serializer = UserProfileSerializer(target_user)
                response_data = {
                    "status": 200,
                    "message": "마이페이지 조회 완료",
                    "data": {
                        "image": user_serializer.data['image'],
                        "nickname": user_serializer.data['nickname'],
                        "recipes": recipe_serializer.data
                    }
                }
            else:
                response_data = {
                    "status": 200,
                    "message": "마이페이지 조회 완료",
                    "data": {
                        "recipes": recipe_serializer.data
                    }
                }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"status": 500, "message": "알 수 없는 오류", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AlertEnableSettingView(APIView):
    def put(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
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
