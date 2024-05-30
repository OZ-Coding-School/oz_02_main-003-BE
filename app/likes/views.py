from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

class LikeToggleView(APIView):

    def post(self, request):
        data = request.data
        return Response(data)