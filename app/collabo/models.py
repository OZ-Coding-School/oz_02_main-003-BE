from django.db import models
from common.models import CommonDateModel
from users.models import User
from ingredients.models import Ingredient
from recipes.models import Recipe


class Fridge(CommonDateModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_fridges"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredient_fridges"
    )


class Group(CommonDateModel):
    GENDER_CHOICES = [
        (False, "Male"),
        (True, "Female"),
    ]
    AGE_CHOICES = [
        (10, "10대"),
        (20, "20대"),
        (30, "30대"),
        (40, "40대"),
        (50, "50대"),
        (60, "60대 이상"),
    ]
    gender = models.BooleanField(choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(choices=AGE_CHOICES)


class Interaction(CommonDateModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    type = models.CharField(max_length=255, default="Click")


class Score(CommonDateModel):

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    score = models.PositiveBigIntegerField()


class RecipeSimilarity(CommonDateModel):
    recipe = models.ForeignKey(
        Recipe, related_name="recipe_id", on_delete=models.CASCADE
    )
    similar_recipe = models.ForeignKey(
        Recipe, related_name="similarities", on_delete=models.CASCADE
    )
    similarity_score = models.FloatField()
