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


# 유저가 가장 최근에 클릭한 레시피 5개 가져오기
def get_recent_interactions(user):
    user_id = user

    # 중복을 제외하고 interaction_id 순서대로 상위 5개 가져오기
    recent_interactions = (
        Interaction.objects.filter(user_id=user_id)
        .order_by('-id')
        .values('recipe_id')
        [:5]
    )

    print(recent_interactions)
    recipe = recent_interactions