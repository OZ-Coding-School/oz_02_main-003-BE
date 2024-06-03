from django.db import models
from users.models import User
from recipes.models import Recipe
from common.models import CommonDateModel

# Create your models here.


class Alert(CommonDateModel):
    CHOICES = [
        (1, "Like"),
        (2, "Comment"),
        (3, "Bookmark"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    type = models.PositiveIntegerField(choices=CHOICES, default=1)
    status = models.BooleanField(default=False)
