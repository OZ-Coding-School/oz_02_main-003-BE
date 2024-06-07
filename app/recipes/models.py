from django.db import models
from common.models import CommonDateModel
from users.models import User
from ingredients.models import Ingredient


class Recipe(CommonDateModel):
    CHOICES = [
        (1, "daily"),
        (2, "healthy"),
        (3, "desert"),
        (4, "midnight_snack"),
        (5, "none"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=40, null=True, blank=True)
    category = models.PositiveIntegerField(choices=CHOICES, default=5)
    story = models.CharField(max_length=255, null=True, blank=True)
    main_image = models.URLField()  # 필수 필드

    def __str__(self):
        return self.title


class Unit(CommonDateModel):
    id = models.PositiveIntegerField(primary_key=True)
    unit = models.CharField(max_length=20, null=True, blank=True)


class Recipe_ingredient(CommonDateModel):
    recipe = models.ForeignKey(
        Recipe, related_name="recipe_ingredient", on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    unit = models.ForeignKey(
        Unit, related_name="unit_recipe_ingredients", on_delete=models.CASCADE
    )

    quantity = models.IntegerField(null=True, blank=True)


class Recipe_step(CommonDateModel):
    recipe = models.ForeignKey(
        Recipe, related_name="recipe_step", on_delete=models.CASCADE
    )

    step = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(null=True, default=None)
