from collabo.models import Interaction
from users.models import User
from .utils import get_group_id

def create_interaction(user, recipe):
    user = User.objects.get(id=user.id)
    age = user.age
    gender = user.gender
    recipe_id = recipe.id

    group_id = get_group_id(age, gender)

    Interaction.objects.create(
        user=user,
        group_id=group_id,
        recipe_id=recipe_id,
    )