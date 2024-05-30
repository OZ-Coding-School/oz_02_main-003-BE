from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

class FridgeView(APIView):

    def get(self, request):
        return Response({"얍": "얍"})
    
class FridgeIngredientAddView(APIView):

    def post(self, request):
        data = request.data
        return Response(data)