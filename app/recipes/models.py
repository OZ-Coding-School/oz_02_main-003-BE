from django.db import models
from common.models import CommonDateModel
from users.models import User
from ingredients.models import Ingredient
from .utils import upload_image, temp_upload_image, upload_image_step


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
    main_image = models.ImageField(upload_to=upload_image, null=True)  # 필수 필드

    def __str__(self):
        return f"{self.id}: {self.title}"


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
    order = models.PositiveIntegerField(null=True)
    image = models.ImageField(upload_to=upload_image_step, null=True)


class Temp_recipe(CommonDateModel):
    CHOICES = [
        (1, "daily"),
        (2, "healthy"),
        (3, "desert"),
        (4, "midnight_snack"),
        (5, "none"),
    ]

    STATUS_CHOICES = [
        (0, "done"),
        (1, "write"),
        (2, "update"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=40, null=True, blank=True)
    category = models.PositiveIntegerField(choices=CHOICES, default=5)
    story = models.CharField(max_length=255, null=True, blank=True)
    main_image = models.ImageField(upload_to=temp_upload_image, null=True)  # 필수 필드
    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=1)
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, null=True, default=None
    )


class Temp_ingredient(CommonDateModel):
    recipe = models.ForeignKey(
        Temp_recipe, related_name="temp_ingredient", on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    unit = models.ForeignKey(
        Unit, related_name="temp_unit_recipe_ingredients", on_delete=models.CASCADE
    )

    quantity = models.IntegerField(null=True, blank=True)


class Temp_step(CommonDateModel):
    recipe = models.ForeignKey(
        Temp_recipe, related_name="temp_step", on_delete=models.CASCADE
    )

    step = models.CharField(max_length=255, null=True, blank=True)
    order = models.PositiveIntegerField(null=True)
    image = models.ImageField(upload_to=temp_upload_image, null=True)


class Updated_recipe(CommonDateModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    done = models.BooleanField(default=False)