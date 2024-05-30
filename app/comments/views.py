from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

class CommentView(APIView):

    def post(self, request):
        data = request.data
        return Response(data)

    def put(self, request):
        data = request.data
        return Response(data)
    
    def delete(self, request):
        return Response({"삭제 요청": "삭제완료"})