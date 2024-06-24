from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from .models import Recipe, Recipe_ingredient, Recipe_step
from .serializers import RecipeSerializer, Recipe_stepSerializer
from ingredients.models import Ingredient
from bookmarks.models import Bookmark
from likes.models import Like
from comments.models import Comment
from users.models import User

from collabo.utils.interaction_utils import create_interaction

class RecipeRecommendView(APIView):
    def post(self, request):
        # 요청에서 사용자가 입력한 재료 ID 목록 가져오기
        user_id = request.user.id
        if not user_id:
            return Response(
                {"status": 400, "message": "사용자 인증이 필요합니다."}, status=400
            )

            return Response(
                {"status": 400, "message": "사용자 인증이 필요합니다."}, status=400
            )

        data = request.data
        ingredient_ids = data.get("ingredients", [])

        # 입력된 재료 ID로 실제 재료 객체 조회
        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        # 조회된 재료 객체의 이름 목록 생성
        ingredient_names = [ingredient.name for ingredient in ingredients]

        # 입력된 재료를 포함하는 레시피 목록 조회
        ## 유사도에서 
        recipes = Recipe.objects.filter(
            recipe_ingredient__ingredient__in=ingredients
        ).distinct()

        # 레시피 정보를 담을 리스트 초기화
        recipe_data = []
        for recipe in recipes:
            # 레시피 작성자 정보 가져오기
            user = User.objects.get(id=recipe.user_id)
            # 레시피 좋아요 수 가져오기
            like = Like.objects.filter(recipe_id=recipe.id).count()
            # 레시피 북마크 수 가져오기
            bookmark = Bookmark.objects.filter(recipe_id=recipe.id).count()

            # 사용자의 좋아요 및 북마크 상태 확인
            like_status = (
                Like.objects.filter(recipe_id=recipe.id, user_id=user_id)
                .values_list("id", flat=True)
                .first()
            )
            if like_status:
                like_status = 1
            else:
                like_status = -1

            bookmark_status = (
                Bookmark.objects.filter(recipe_id=recipe.id, user_id=user_id)
                .values_list("id", flat=True)
                .first()
            )
            if bookmark_status:
                bookmark_status = 1
            else:
                bookmark_status = -1

            # 레시피에 포함된 재료 이름 목록 생성
            recipe_ingredients = [
                item.ingredient.name for item in recipe.recipe_ingredient.all()
            ]

            # 입력된 재료 중 레시피에 포함된 재료와 포함되지 않은 재료 구분
            include_ingredients = [
                name for name in ingredient_names if name in recipe_ingredients
            ]
            not_include_ingredients = [
                name for name in recipe_ingredients if name not in include_ingredients
            ]

            recipe_info = {
                "recipe_id": recipe.id,
                "nickname": user.nickname,
                "include_ingredients": include_ingredients,
                "not_include_ingredients": not_include_ingredients,
                "title": recipe.title,
                "likes": like,
                "bookmark": bookmark,
                "like_status": like_status,
                "bookmark_status": bookmark_status,
            }
            recipe_data.append(recipe_info)

        response_data = {
            "status": 200,
            "message": "조회 성공",
            "data": {"ingredients": ingredient_names, "recipes": recipe_data},
        }

        # 응답 반환
        return Response(response_data)


from .models import Temp_recipe, Temp_step, Unit
from .utils import create_file
from common.utils.image_utils import get_image_uri


class CreateTempImage(APIView):
    def post(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"status": "400", "message": "토큰이 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        actions = request.data.get("action")
        if actions != "write":
            return Response(
                {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
            )

        if "image" not in request.data:
            return Response(
                {"error": "No image data provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        image_data = request.data["image"]
        type_data = request.data.get("type")
        order = request.data.get("order")

        if type_data not in ["main", "step"]:
            return Response(
                {"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST
            )

        image_file = None
        if image_data:
            try:
                format, imgstr = image_data.split(";base64,")
                ext = format.split("/")[-1]
                image_file = create_file(type_data, ext, imgstr, order)
            except ValueError:
                return Response(
                    {"error": "Invalid image data format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        if type_data == "main":
            temp_recipe, _ = Temp_recipe.objects.get_or_create(
                user_id=user.id, status=1
            )
            temp_recipe.main_image = image_file
            temp_recipe.save()

            data = {
                "status": 201,
                "message": "임시 레시피 이미지 저장 성공",
                "data": {
                    "id": temp_recipe.id,
                    "image": (
                        temp_recipe.main_image.url if temp_recipe.main_image else None
                    ),
                },
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            temp_recipe = Temp_recipe.objects.filter(user_id=user.id, status=1).last()

            if not temp_recipe:
                return Response(
                    {"error": "유효한 Temp_recipe를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            temp_step, _ = Temp_step.objects.get_or_create(
                recipe=temp_recipe, order=order
            )
            temp_step.image = image_file
            temp_step.save()

            data = {
                "status": 201,
                "message": "임시 레시피 이미지 저장 성공",
                "data": {
                    "id": temp_step.id,
                    "image": temp_step.image.url if temp_step.image else None,
                },
            }
            return Response(data, status=status.HTTP_201_CREATED)


import os
from .utils import copy_file
from config.settings import BUCKET_PATH


class CreateRecipe(APIView):
    def post(self, request):
        user_id = request.user.id
        if not user_id:
            return Response(
                {"status": 400, "message": "사용자 인증이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            temp_recipe = Temp_recipe.objects.filter(user_id=user_id, status=1).first()

            if not temp_recipe:
                return Response(
                    {"error": "Temporary recipe not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 요청 데이터를 복사하여 수정 가능하게 만듭니다.
            data = request.data.copy()

            recipe_ingredients_data = data.pop("recipe_ingredients", [])
            steps_data = data.pop("steps", [])

            recipe = Recipe.objects.create(user_id=user_id, **data)
            temp_recipe.recipe = recipe
            temp_recipe.save()

            # recipe_ingredients 데이터 처리
            for ingredient_data in recipe_ingredients_data:
                ingredient_name = ingredient_data.get("name", None)
                unit_id = ingredient_data.get("unit")
                quantity = ingredient_data.get("quantity")

                # 재료를 DB에서 찾거나 없으면 새로 생성
                try:
                    ingredient = Ingredient.objects.get(name=ingredient_name)
                except Ingredient.DoesNotExist:
                    # 존재하지 않는 경우 새로운 재료 생성
                    ingredient = Ingredient.objects.create(name=ingredient_name)

                # 단위 객체 가져오기
                unit = Unit.objects.get(id=unit_id)

                # RecipeIngredient 생성
                Recipe_ingredient.objects.create(
                    recipe=recipe, ingredient=ingredient, quantity=quantity, unit=unit
                )

            if temp_recipe.main_image:
                main_image_source = temp_recipe.main_image.name
                main_image_dest = f"{BUCKET_PATH}recipe/{recipe.id}/{os.path.basename(main_image_source)}"
                copy_file(main_image_source, main_image_dest)

                recipe.main_image = main_image_dest
                recipe.save()

            temp_steps = Temp_step.objects.filter(recipe=temp_recipe).order_by("order")
            count = 0

            for i, step_text in enumerate(steps_data, 1):
                temp_image = None
                if temp_steps and count < len(temp_steps):
                    if i == temp_steps[count].order:
                        temp_image = temp_steps[count].image
                        count += 1

                step_data = {"recipe": recipe.id, "step": step_text}
                step_serializer = Recipe_stepSerializer(data=step_data)

                if step_serializer.is_valid():
                    recipe_step = step_serializer.save()
                    if temp_image:
                        temp_image_source = temp_image.name
                        temp_image_dest = f"{BUCKET_PATH}recipe/{recipe.id}/{os.path.basename(temp_image_source)}"
                        copy_file(temp_image_source, temp_image_dest)

                        recipe_step.image = temp_image_dest
                        recipe_step.save()
                else:
                    print("Errors:", step_serializer.errors)

            # temp_recipe 상태 업데이트
            temp_recipe.status = 0
            temp_recipe.save()

            response_data = {
                "status": 201,
                "message": "레시피 작성 성공",
                "data": {"id": recipe.id},
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecipeDetailDeleteView(APIView):
    def get(self, request, id):
        try:
            recipe = Recipe.objects.get(pk=id)
            bookmarks_count = Bookmark.objects.filter(recipe_id=id).count()
            likes_count = Like.objects.filter(recipe_id=id).count()

            # 테스트용 user_id 하드코딩
            user = request.user
            if user:

                like_status = Like.objects.filter(recipe_id=id, user_id=user.id).first()

                bookmark_status = Bookmark.objects.filter(
                    recipe_id=id, user_id=user.id
                ).first()

            like_status = 1 if user and like_status else -1
            bookmark_status = 1 if user and bookmark_status else -1

            # is_staff 값이 True이거나 user.id가 본인이면 canUpdate를 1로 설정
            if user and (user.is_staff or user.id == recipe.user.id):
                can_update = 1
            else:
                can_update = 0

            ingredients = Recipe_ingredient.objects.filter(recipe_id=id).order_by("id")
            steps = Recipe_step.objects.filter(recipe_id=id).order_by("id")
            comments = (
                Comment.objects.filter(recipe_id=id)
                .select_related("user")
                .values(
                    "id",
                    "user__id",
                    "user__nickname",
                    "updated_at",
                    "comment",
                    "user__image",
                )
                .order_by("id")
            )

            # 각 댓글의 can_update 값 설정
            comment_data = []
            for comment in comments:
                if user and (user.is_staff or comment["user__id"] == user.id):
                    comment_can_update = 1
                else:
                    comment_can_update = 0
                comment_data.append(
                    {
                        "id": comment["id"],
                        "user_id": comment["user__id"],
                        "user_nickname": comment["user__nickname"],
                        "profile_image": get_image_uri(comment["user__image"]),
                        "updated_at": comment["updated_at"],
                        "comment": comment["comment"],
                        "can_update": comment_can_update,
                    }
                )

            serializer = RecipeSerializer(recipe)
            data = {
                "status": status.HTTP_200_OK,
                "message": "레시피 조회 성공",
                "data": {
                    "can_update": can_update,
                    **serializer.data,
                    "like": likes_count,
                    "like_status": like_status,
                    "book": bookmarks_count,
                    "book_status": bookmark_status,
                    "user": {
                        "id": recipe.user.id,
                        "nickname": recipe.user.nickname,
                        "profile_image": get_image_uri(recipe.user.image),
                        "date": recipe.updated_at,
                    },
                    "ingredients": [
                        {
                            "id": ingredient.id,
                            "name": ingredient.ingredient.name,
                            "quantity": ingredient.quantity,
                            "unit": ingredient.unit.unit,
                        }
                        for ingredient in ingredients
                    ],
                    "steps": [
                        {
                            "step": step.step,
                            "image": step.image.url if step.image else "",
                        }
                        for step in steps
                    ],
                    "comments": comment_data,
                },
            }

            create_interaction(user, recipe)

            return Response(data)
        except Recipe.DoesNotExist:
            return Response(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": f"ID {id}에 해당하는 레시피를 찾을 수 없습니다.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def get_object(self, id):
        try:
            return Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise NotFound(f"ID {id}에 해당하는 레시피를 찾을 수 없습니다.")

    def delete(self, request, id):
        recipe = self.get_object(id)
        recipe.delete()
        data = {"status": 200, "message": "레시피 삭제 성공"}
        return Response(data, status=status.HTTP_200_OK)

from collabo.utils.similary_utils import get_recommend_recipes

class RecipeCategoryListView(APIView):
    def get_category_name(self, category):
        category_mapping = {
            "daily": "1",
            "healthy": "2",
            "desert": "3",
            "midnight": "4",
        }
        return category_mapping.get(category, None)

    def get(self, request, category=None):
        user_id = request.user.id  # 현재 사용자의 ID 가져오기
        category_name = self.get_category_name(category)

        if category == "like":
            # 사용자가 좋아요를 누른 레시피만 필터링
            filtered_recipes = Recipe.objects.filter(like__user_id=user_id)
        elif category == "book":
            # 사용자가 북마크한 레시피만 필터링
            filtered_recipes = Recipe.objects.filter(bookmark__user_id=user_id)
        elif category_name:
            similar_recipes, updated_recipes = get_recommend_recipes(user_id)
            filtered_similar_recipes = similar_recipes.filter(category=category_name)
            filtered_updated_recipes = updated_recipes.filter(category=category_name) if updated_recipes else []
            filtered_recipes = list(filtered_similar_recipes) + list(filtered_updated_recipes)
        else:
            return Response(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "유효한 카테고리가 아닙니다.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        limit_recipe = filtered_recipes
        recipe_data = []
        for recipe in limit_recipe:
            user = User.objects.get(id=recipe.user_id)
            like = Like.objects.filter(recipe_id=recipe.id, user_id=user_id).first()
            book = Bookmark.objects.filter(recipe_id=recipe.id, user_id=user_id).first()

            like_status = 1 if like else -1
            book_status = 1 if book else -1

            recipe_info = {
                "id": recipe.id,
                "user": user.nickname,
                "title": recipe.title,
                "main_image": recipe.main_image.url,
                "like": Like.objects.filter(recipe_id=recipe.id).count(),
                "like_status": like_status,
                "book": Bookmark.objects.filter(recipe_id=recipe.id).count(),
                "book_status": book_status,
            }
            recipe_data.append(recipe_info)

        response_data = {
            "status": 200,
            "message": (
                "카테고리 레시피 조회 성공"
                if category_name
                else "좋아요 및 북마크 레시피 조회 성공"
            ),
            "data": recipe_data,
        }

        return Response(response_data)


class RecipeSearchKeywordView(APIView):
    def get(self, request, keyword):
        user_id = request.user.id
        if not keyword:
            return Response({"message": "검색어를 입력해 주세요."}, status=400)

        similar_recipes, updated_recipes = get_recommend_recipes(user_id)
        filtered_similer_recipes = similar_recipes.filter(
            Q(title__icontains=keyword)
            | Q(recipe_ingredient__ingredient__name__icontains=keyword)
        ).distinct()
        filtered_updated_recipes = updated_recipes.filter(
            Q(title__icontains=keyword)
            | Q(recipe_ingredient__ingredient__name__icontains=keyword)
        ).distinct()

        filtered_recipes = list(filtered_similer_recipes) + list(filtered_updated_recipes)

        if not filtered_recipes:
            return Response({"message": "해당되는 레시피가 없습니다."}, status=404)

        recipe_data = []
        for recipe in filtered_recipes:
            user = User.objects.get(id=recipe.user_id)
            like = Like.objects.filter(recipe_id=recipe.id, user_id=user_id).first()
            book = Bookmark.objects.filter(recipe_id=recipe.id, user_id=user_id).first()

            like_status = 1 if like else -1
            book_status = 1 if book else -1

            recipe_info = {
                "id": recipe.id,
                "user": user.nickname,
                "title": recipe.title,
                "main_image": recipe.main_image.url,
                "like": Like.objects.filter(recipe_id=recipe.id).count(),
                "like_status": like_status,
                "book": Bookmark.objects.filter(recipe_id=recipe.id).count(),
                "book_status": book_status,
            }
            recipe_data.append(recipe_info)

        response_data = {
            "status": 200,
            "message": "레시피 조회 성공",
            "data": recipe_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


from django.db.models import F


class RecipeStep(APIView):
    def delete(self, request, order):
        user_id = request.user.id

        try:
            # 사용자의 임시 레시피에서 order 값이 일치하는 레코드 찾기
            temp_recipe = Temp_recipe.objects.filter(user_id=user_id, status=1).first()
            if not temp_recipe:
                return Response(
                    {"error": "Temporary recipe not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            temp_step = Temp_step.objects.filter(
                recipe=temp_recipe, order=order
            ).first()
            if temp_step:
                temp_step.delete()

            Temp_step.objects.filter(recipe=temp_recipe, order__gt=order).update(
                order=F("order") - 1
            )

            return Response(
                {"status": 200, "message": "레시피 단계가 삭제되었습니다."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
