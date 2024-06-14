from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert
from likes.models import Like
from bookmarks.models import Bookmark
from comments.models import Comment


def create_alert(type, recipe, target_user, trigger_user):
    Alert.objects.create(
        target_user=target_user,
        trigger_user=trigger_user,
        recipe=recipe,
        type=type,
    )

def get_users(instance):
    target_user = instance.recipe.user
    trigger_user = instance.user

    return target_user, trigger_user

@receiver(post_save, sender=Like)
def create_alert_on_like(sender, instance, created, **kwargs):
    if created:
        target_user, trigger_user = get_users(instance)
        if(target_user != trigger_user) and target_user.is_alert:
            create_alert(1, instance.recipe, target_user, trigger_user)


@receiver(post_save, sender=Comment)
def create_alert_on_comment(sender, instance, created, **kwargs):
    if created:
        target_user, trigger_user = get_users(instance)
        if(target_user != trigger_user) and target_user.is_alert:
            create_alert(2, instance.recipe, target_user, trigger_user)


@receiver(post_save, sender=Bookmark)
def create_alert_on_bookmark(sender, instance, created, **kwargs):
    if created:
        target_user, trigger_user = get_users(instance)
        if(target_user != trigger_user) and target_user.is_alert:
            create_alert(3, instance.recipe, target_user, trigger_user)
