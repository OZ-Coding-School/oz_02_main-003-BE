from django.db import models
from common.models import CommonDateModel
from users.models import User
from ingredients.models import Ingredient


class Recipe(CommonDateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=40, null=True, blank=True)
    category = models.CharField(max_length=20, null=True, blank=True)
    story = models.CharField(max_length=255, null=True, blank=True)
    like_count = models.IntegerField(default=0, null=True, blank=True)
    bookmark_count = models.IntegerField(default=0, null=True, blank=True)
    comment_count = models.IntegerField(default=0, null=True, blank=True)
    image_1 = models.URLField()  # 필수 필드
    image_2 = models.URLField(null=True, default=None)  # 선택 필드
    image_3 = models.URLField(null=True, default=None)  # 선택 필드

    def __str__(self):
        return self.title


class Unit(CommonDateModel):
    id = models.PositiveIntegerField(primary_key=True)
    unit = models.CharField(max_length=20, null=True, blank=True)


class Recipe_ingredient(CommonDateModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    unit = models.ForeignKey(
        Unit, related_name="unit_recipe_ingredients", on_delete=models.CASCADE
    )

    quantity = models.IntegerField(null=True, blank=True)


class Recipe_step(CommonDateModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    step = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(null=True, default=None)
