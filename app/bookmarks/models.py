from django.db import models
from common.models import CommonDateModel
from users.models import User
from recipes.models import Recipe


# Create your models here.
class Bookmark(CommonDateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
