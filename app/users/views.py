from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone

from .services import SocialLoginServices, SocialLoginCallbackServices


from users.models import User_refresh_token

User = get_user_model()


class LoginView(APIView):
    def get(self, request):
        social_types = ("kakao", "google")

        # 소셜로그인인지 확인
        social_type = request.GET.get("social", None)

        if social_type is not None and social_type not in social_types:
            return Response({"status": 400, "message": "잘못된 소셜 타입"}, status=400)
        if social_type in social_types:
            return SocialLoginServices.get_social_login_redirect_object(social_type)

        # 토큰 존재하면 토큰 사용 로그인
        token = request.COOKIES.get("ndd_access", None)
        if token:
            # 액세스 토큰은 유효기간이 짧아 기간이 지났을 거니까 valid 통과 불가
            # 토큰을 분해해서 유저 id 가져오기
            # 유저 id를 통해 refresh 토큰있나 확인

            from rest_framework_simplejwt.tokens import RefreshToken
            from rest_framework_simplejwt.tokens import AccessToken
            import jwt

            try:
                user_id = jwt.decode(token, options={"verify_signature": False})[
                    "user_id"
                ]
            except:
                response = Response(
                    {"status": 401, "message": "유효하지 않은 토큰입니다"}, status=401
                )
                response.delete_cookie("ndd_access")
                return response

            try:
                refresh_token = User_refresh_token.objects.get(id=user_id).token
                refresh = RefreshToken(refresh_token)
            except User_refresh_token.DoesNotExist:
                response = Response(
                    {"status": 401, "message": "다시 로그인 해주시기 바랍니다"},
                    status=401,
                )
                response.delete_cookie("ndd_access")
                return response

            return Response({"ndd_access": token})

        else:
            return Response({"status": 400, "message": "토큰이 없습니다."}, 400)


class LoginCallbackView(APIView):
    def get(self, request, social):
        data = request.query_params.copy()

        code = data.get("code")
        if not code:
            return Response(status=400)

        slcs = SocialLoginCallbackServices(social)

        # social_token 발급 요청
        social_token = slcs.get_social_token(code)
        # social_token 을 통해 user 객체 가져오기(or 생성)
        user = slcs.get_user(social_token)
        # 가져온 user 객체를 통해 access_token 생성
        access_token = slcs.get_access_token(user)

        response = Response({"status": 200, "message": "로그인 성공"})
        response.set_cookie("ndd_access", access_token, httponly=True)

        user.last_login = timezone.now()
        user.save()

        return response


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
