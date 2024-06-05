from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import User
from recipes.models import Recipe
from .serializers import RecipeSerializer
from django.shortcuts import get_object_or_404
from bookmarks.models import Bookmark
from likes.models import Like
from django.db.models import Count
from django.db.models import Subquery, OuterRef, Count
class MainPageView(APIView):
    def get_best_recipes(self):
        likes_subquery = Like.objects.filter(recipe=OuterRef('pk')).order_by().values('recipe').annotate(cnt=Count('pk')).values('cnt')
        return Recipe.objects.annotate(likes_count=Subquery(likes_subquery)).order_by('-likes_count')[:1]
    
    def get_best_bookmarked_recipes(self):
        bookmarks_subquery = Bookmark.objects.filter(recipe=OuterRef('pk')).order_by().values('recipe').annotate(cnt=Count('pk')).values('cnt')
        return Recipe.objects.annotate(bookmarks_count=Subquery(bookmarks_subquery)).order_by('-bookmarks_count')[:1]

    def get_category_recipes(self, category_id):
        likes_subquery = Like.objects.filter(recipe=OuterRef('pk')).order_by().values('recipe').annotate(cnt=Count('pk')).values('cnt')
        return Recipe.objects.filter(category=category_id).annotate(likes_count=Subquery(likes_subquery))[:4]
    
    def get(self, request):
        best_recipes = self.get_best_recipes()
        best_serializer = RecipeSerializer(best_recipes, many=True)

        best_bookmarked_recipes = self.get_best_bookmarked_recipes()
        best_bookmarked_serializer = RecipeSerializer(best_bookmarked_recipes, many=True)

        daily_recipes = self.get_category_recipes(category_id=1)
        daily_serializer = RecipeSerializer(daily_recipes, many=True)

        healthy_recipes = self.get_category_recipes(category_id=2)
        healthy_serializer = RecipeSerializer(healthy_recipes, many=True)

        desert_recipes = self.get_category_recipes(category_id=3)
        desert_serializer = RecipeSerializer(desert_recipes, many=True)

        midnight_snack_recipes = self.get_category_recipes(category_id=4)
        midnight_snack_serializer = RecipeSerializer(midnight_snack_recipes, many=True)

        return Response({
            "status": 200,
            "message": "조회 성공",
            "data": {
                "best": best_serializer.data,
                "best_bookmarked": best_bookmarked_serializer.data,
                "daily": daily_serializer.data,
                "healthy": healthy_serializer.data,
                "desert": desert_serializer.data,
                "midnightSnack": midnight_snack_serializer.data,
            }
        })