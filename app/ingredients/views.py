from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

class IngredientTypeView(APIView):

    def get(self, request, type):
        return Response({"type": type})
    
class IngredientTypeSearchView(APIView):

    def get(self, request, type, search):
        return Response({
            "type": type,
            "search": search,
            })