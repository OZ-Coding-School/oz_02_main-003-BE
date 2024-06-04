from users.models import User, User_refresh_token
from django.utils import timezone


def get_or_create_social_user(type, id, image=None):
    social_id = f"{type}_{id}"
    data = {"social_type": type, "social_id": social_id, "image": image}
    user, _ = User.objects.get_or_create(**data)
    user.nickname = f"{user.id}번째 냉장고"
    user.save()
    return user


def update_or_create_refresh_token_data(user, token):
    """
    DB에 Refresh Token 수정 또는 생성
    """
    new_refresh_token_data = {
        "user": user,
        "token": str(token),
        "estimate": timezone.now() + token.lifetime,
    }

    User_refresh_token.objects.update_or_create(
        defaults=new_refresh_token_data, **{"user": user}
    )
