from django.shortcuts import render
from rest_framework.views import APIView
from .utils.interaction_utils import get_recent_interactions
from rest_framework.response import Response

class TestView(APIView):
    def get(self, request):
        user = 2

        get_recent_interactions(user)

        return Response("굿")


