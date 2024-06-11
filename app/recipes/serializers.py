from rest_framework import serializers
from .models import Recipe, Recipe_ingredient, Recipe_step, Unit
from ingredients.models import Ingredient
from users.models import User

class Recipe_stepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe_step
        fields = ['id', 'step', "recipe"]


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['title', 'main_image', 'category', 'story']
        
    def update(self, instance, validated_data):
        # 외래 키로 사용할 User 객체를 하드코딩으로 가져옴
        user = User.objects.get(id=1)

        # recipe_ingredients와 recipe_steps 데이터는 request 데이터에서 직접 가져옴
        recipe_ingredients_data = self.initial_data.get('recipe_ingredients', [])
        recipe_steps_data = self.initial_data.get('steps', [])

        # Recipe 객체 업데이트
        instance.title = validated_data.get('title', instance.title)
        instance.main_image = validated_data.get('main_image', instance.main_image)
        instance.category = validated_data.get('category', instance.category)
        instance.story = validated_data.get('story', instance.story)
        instance.save()

        # Recipe_ingredient 객체 업데이트
        instance.recipe_ingredient.all().delete()
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
        instance.recipe_step.all().delete()
        for step_data in recipe_steps_data:
            Recipe_step.objects.create(
                recipe=instance,
                step=step_data,
            )

        return instance