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

    def __str__(self):
        return f"{self.user}'s fridge contains {self.ingredient}"


class Interaction(CommonDateModel):
    INTERACTION_TYPE_CHOICES = [
        (1, "Click"),
        (2, "Favorite"),
        (3, "Like"),
        (4, "Comment"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_interactions"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_interactions"
    )
    type = models.PositiveIntegerField(choices=INTERACTION_TYPE_CHOICES)

    def __str__(self):
        return f"{self.get_type_display()} by {self.user} on {self.recipe}"
