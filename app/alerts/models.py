from django.db import models
from users.models import User
from recipes.models import Recipe
from common.models import CommonDateModel

# Create your models here.


class Alert(CommonDateModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    
    type = models.PositiveIntegerField(null=True, blank=True)
    status = models.BooleanField(null=True, default=None)
