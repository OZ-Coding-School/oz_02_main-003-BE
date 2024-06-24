from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Recipe, Updated_recipe

@receiver(post_save, sender=Recipe)
def create_updated_recipe_on_recipe(sender, instance, created, **kwargs):
    if created:
        Updated_recipe.objects.create(status='new', recipe=instance)