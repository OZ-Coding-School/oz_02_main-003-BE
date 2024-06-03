from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from alerts.models import Alert
from users.models import User
from .serializers import AlertSerializer


class UserAlertsView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        alerts = Alert.objects.filter(user=user).order_by("-created_at")
        serializer = AlertSerializer(alerts, many=True)

        return Response(
            {
                "status": 200,
                "message": "알림 데이터 조회 완료",
                "created_at": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UnreadUserAlertsView(APIView):
    def get(self, request):
        # 사용자 인증 확인
        # if not user.is_authenticated:
        #     return Response({'status': 403, 'message': '인증되지 않은 사용자입니다.'}, status=403)
        user_id = 1  # 테스트 목적으로 사용자 ID를 1로 설정

        # 가장 최근에 생성된 알람 가져오기
        alert_exists = Alert.objects.filter(user_id=user_id, status=1).exists()

        if alert_exists:
            # status가 1인 알람이 존재하면, 성공 메시지와 함께 그 정보를 반환
            return Response(
                {
                    "status": 200,
                    "message": "읽지 않은 알림 존재 존재합니다.",
                },
                status=200,
            )
        else:
            # status가 1인 알람이 없으면, 알림 메시지를 반환
            return Response(
                {
                    "status": 404,
                    "message": "알람이 존재하지 않습니다.",
                },
                status=404,
            )
