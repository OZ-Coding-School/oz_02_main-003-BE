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
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.id != user_id:
            return Response(
                {"status": 403, "message": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        alerts = Alert.objects.filter(user=user).order_by("-created_at")
        serializer = AlertSerializer(alerts, many=True)

        return Response(
            {
                "status": 200,
                "message": "알림 데이터 조회 완료",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UnreadUserAlertsView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 사용자에게 온 모든 읽지 않은 알림 가져오기
        unread_alerts = Alert.objects.filter(user=user, status=1)

        if unread_alerts.exists():
            # 사용자에게 온 모든 읽지 않은 알림을 시리얼라이즈하여 반환
            serializer = AlertSerializer(unread_alerts, many=True)
            # status가 True인 레시피의 id와 status 필드를 선택하여 반환
            unread_alerts_data = [
                {"recipe_id": item["recipe_id"], "status": item["status"]}
                for item in serializer.data
                if item["status"]
            ]
            return Response(
                {
                    "status": 200,
                    "message": "읽지 않은 알림이 존재합니다.",
                    "data": unread_alerts_data,
                },
                status=200,
            )
        else:
            # 읽지 않은 알림이 없으면, 알림이 존재하지 않음을 반환
            return Response(
                {"status": 404, "message": "읽지 않은 알림이 존재하지 않습니다."},
                status=404,
            )
