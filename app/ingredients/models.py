from django.db import models
from common.models import CommonDateModel


class Ingredient(CommonDateModel):

    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(null=True, default=None)
