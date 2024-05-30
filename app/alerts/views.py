from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

class UserAlertsView(APIView):

    def get(self, request):
        return Response({"알람 목록": "잘 된다"})
    
class UnreadUserAlertsView(APIView):

    def get(self, request):
        return Response({"읽지않은 알람 목록": "잘 된다"})