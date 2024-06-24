from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Alert
from .serializers import AlertSerializer
from datetime import timedelta
from django.utils import timezone


class UserAlertsView(APIView):
    def get(self, request):
        user = request.user
        
        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        two_weeks_ago = timezone.now() - timedelta(weeks=2)
        alerts = Alert.objects.filter(target_user=user).exclude(status=0, created_at__lt=two_weeks_ago).order_by("-created_at")
        
        serializer = AlertSerializer(alerts, many=True)
        return Response(
            {
                "status": 200,
                "message": "알림 데이터 조회 완료",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    
    def post(self, request):
        user = request.user
        if not user:
            return Response(
                {"status": 400, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alerts = request.data.get("alerts")

        if not alerts:
            return Response(
                {"status": 400, "message": "알림 데이터를 넣어주시기 바랍니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipe_ids = []

        for alert_id in alerts:
            try:
                alert_obj = Alert.objects.get(id=alert_id, target_user=user)
                alert_obj.status = False  # 알림을 읽음으로 표시
                alert_obj.save()
                recipe_ids.append(alert_obj.recipe_id)
            except Alert.DoesNotExist:
                return Response(
                    {
                        "status": 400,
                        "message": f"ID가 {alert_id}인 알림은 유저의 알림이 아닙니다.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"status": 200, "message": "알림 확인 처리 완료", "data": recipe_ids}, 
            status=status.HTTP_200_OK
        )


class UnreadUserAlertsView(APIView):
    def get(self, request):
        user = request.user

        if not user:
            return Response(
                {"status": 404, "message": "로그인 된 유저가 아닙니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 현재 로그인한 사용자에게 도착한 읽지 않은 알림들 가져오기
        unread_alerts = Alert.objects.filter(target_user=user, status=True)
        alert_status = False
        if unread_alerts.exists():
            alert_status = True
            # 읽지 않은 알림이 존재할 경우
        return Response(
            {
                "status": 200,
                "message": "읽지 않은 알림 조회 완료.",
                "data": {"status": alert_status},
            },
            status=status.HTTP_200_OK,
        )
