from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import redirect

from .services import SocialLoginServices, SocialLoginCallbackServices


from users.models import User_refresh_token

User = get_user_model()

from users.customs.authentication import CustomCookieAuthentication
from common.data.envdata import ACCESS_TOKEN_COOKIE_NAME


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
            return SocialLoginServices.get_social_login_redirect_object(social_type, dev)

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
        redirect_uri = ["https://ndd-project.vercel.app/", "http://localhost:5173"]
        response = redirect(redirect_uri[dev])
        response.set_cookie("ndd_access", access_token, httponly=True)

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
