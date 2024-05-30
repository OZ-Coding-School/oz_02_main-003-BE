from rest_framework.views import APIView
from rest_framework.response import Response


class KakaoLoginView(APIView):
    def post(self, request):
        # Formatter 생성
        return Response("kakao 로그인 시도")


class GoogleLoginView(APIView):
    def post(self, request):
        return Response("google 로그인 시도")


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
    def put(self,request):
        return Response("닉네임 변경 완료")

class UpdateImageView(APIView):
    def put(self,request):
        return Response("프로필 사진 변경 완료")

class MyPageView(APIView):
    def get(self, request, user_id, scroll_count):
        return Response({"user_id": user_id, "scroll_count": scroll_count})


class AlertEnableSettingView(APIView):
    def put(self, request):
        return Response("알림 설정 완료")
