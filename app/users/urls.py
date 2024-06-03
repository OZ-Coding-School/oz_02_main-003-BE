from django.urls import path
from .views import *

urlpatterns = [
    ### 로그인 ###
    #/api/v1/users/auth/kakao
    path("/auth/kakao", KakaoLoginView.as_view(), name="uesr-auth-kakao"),
    path("/auth/kakao/callback", KakaoLoginCallbackView.as_view(), name="uesr-auth-kakao-callback"),
    #/api/v1/users/auth/google
    path("/auth/google", GoogleLoginView.as_view(), name="user-auth-google"),
    path("/auth/google/callback", GoogleLoginCallbackView.as_view(), name="user-auth-google-callback"),
    #/api/v1/users/auth/login
    path("/auth/login", LoginView.as_view(), name="user-login"),
    #/api/v1/users/auth/logout
    path("/auth/logout", LogoutView.as_view(), name="user-logout"),


    ### 계정 설정 ###
    #/api/v1/users
    path("", UserView.as_view(), name="user"),
    #/api/v1/users/nickname
    path("/nickname", UpdateNicknameView.as_view(), name="user-update-nickname"),
    #/api/v1/users/image
    path("/image", UpdateImageView.as_view(), name="user-update-image"),

    # 알람 설정
    #/api/v1/users/alerts/enabl
    path("/alerts/enable", AlertEnableSettingView.as_view(), name="user-alert-enable"),
    
    ### 마이페이지 ###
    #/api/v1/users/mypage/1/3
    path("/mypage/<int:user_id>/<int:scroll_count>", MyPageView.as_view(), name="user-mypage"),
]