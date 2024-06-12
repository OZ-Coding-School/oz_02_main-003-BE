from django.urls import path
from .views import *

urlpatterns = [
    # ### 로그인 ###
    #/api/v1/users/auth/login
    #/api/v1/users/auth/login?social=kakao
    #/api/v1/users/auth/login?social=google
    path("/auth/login", LoginView.as_view(), name="user-login"),

    #/api/v1/users/auth/login/kakao
    #/api/v1/users/auth/login/google
    path("/auth/login/callback/<str:social>/<int:dev>", LoginCallbackView.as_view(), name="user-login-callback"),
    
    #/api/v1/users/auth/logout
    path("/auth/logout", LogoutView.as_view(), name="user-logout"),


    ### 계정 설정 ###
    #/api/v1/users/detail
    path('/detail', UserDetailView.as_view(), name='user_detail'),
    #/api/v1/users
    path("", UserView.as_view(), name="user"),
    #/api/v1/users/nickname
    path("/nickname", UpdateNicknameView.as_view(), name="user-update-nickname"),
    #/api/v1/users/image
    path("/image", UserImageView.as_view(), name="user-update-image"),
    #/api/v1/users/delete
    path("/delete", UserDeleteView.as_view(), name='user_delete'),
    # 알람 설정
    #/api/v1/users/alerts/enable
    path("/alerts/enable", AlertEnableView.as_view(), name="user-alert-enable"),
    
    ### 마이페이지 ###
    #/api/v1/users/mypage/1/3
    path("/mypage/<int:id>/<int:cnt>", MyPageView.as_view(), name="user-mypage"),
]