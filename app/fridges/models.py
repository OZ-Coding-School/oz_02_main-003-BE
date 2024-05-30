from django.db import models
from common.models import CommonDateModel
from users.models import User
from ingredients.models import Ingredient
# Create your models here.
class Fridge(CommonDateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)