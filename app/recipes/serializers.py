from rest_framework import serializers
from .models import Recipe, Recipe_ingredient, Recipe_step, Unit
from ingredients.models import Ingredient
from users.models import User

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'unit']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']

class Recipe_ingredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()
    unit = UnitSerializer()

    class Meta:
        model = Recipe_ingredient
        fields = ['id', 'ingredient', 'unit', 'quantity']

class Recipe_stepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe_step
        fields = ['id', 'step', 'image']

class RecipeSerializer(serializers.ModelSerializer):
    recipe_ingredients = Recipe_ingredientSerializer(many=True, read_only=True)
    recipe_steps = Recipe_stepSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ['title', 'image_1', 'image_2', 'image_3', 'category', 'recipe_ingredients', 'recipe_steps', 'story']

    def create(self, validated_data):
        # 외래 키로 사용할 User 객체를 하드코딩으로 가져옴
        user = User.objects.get(id=1)

        # recipe_ingredients와 steps 데이터는 request 데이터에서 직접 가져옴
        # 'recipe_ingredients'와 'steps' 데이터 추출
        recipe_ingredients_data = self.initial_data.get('recipe_ingredients')
        recipe_steps_data = self.initial_data.get('steps')

        # Recipe 객체 생성 시 user 필드를 포함하여 생성
        recipe = Recipe.objects.create(user=user, **validated_data)

        for ingredient_data in recipe_ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(name=ingredient_data['name'])
            unit = Unit.objects.get(id=ingredient_data['unit'])
            Recipe_ingredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                unit=unit,
                quantity=ingredient_data['quantity']
            )

        for step_data in recipe_steps_data:
            Recipe_step.objects.create(
                recipe=recipe,
                step=step_data['step'],
                image=step_data.get('image')
            )

        return recipe
    

    def update(self, instance, validated_data):
        # 외래 키로 사용할 User 객체를 하드코딩으로 가져옴
        user = User.objects.get(id=1)

        # recipe_ingredients와 recipe_steps 데이터는 request 데이터에서 직접 가져옴
        recipe_ingredients_data = self.initial_data.get('recipe_ingredients', [])
        recipe_steps_data = self.initial_data.get('steps', [])

        # Recipe 객체 업데이트
        instance.title = validated_data.get('title', instance.title)
        instance.image_1 = validated_data.get('image_1', instance.image_1)
        instance.image_2 = validated_data.get('image_2', instance.image_2)
        instance.image_3 = validated_data.get('image_3', instance.image_3)
        instance.category = validated_data.get('category', instance.category)
        instance.story = validated_data.get('story', instance.story)
        instance.save()

        # Recipe_ingredient 객체 업데이트
        instance.recipe_ingredient_set.all().delete()
        for ingredient_data in recipe_ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ingredient_data['name']
            )
            unit = Unit.objects.get(id=ingredient_data['unit'])
            Recipe_ingredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                unit=unit,
                quantity=ingredient_data['quantity']
            )

        # Recipe_step 객체 업데이트
        instance.recipe_step_set.all().delete()
        for step_data in recipe_steps_data:
            Recipe_step.objects.create(
                recipe=instance,
                step=step_data['step'],
                image=step_data.get('image')
            )

        return instance