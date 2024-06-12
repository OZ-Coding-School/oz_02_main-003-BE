from users.models import User_refresh_token
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

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


import os
import uuid

def generate_image_path(user, ext, bucket_path):
    unique_filename = f"{user.nickname}_{uuid.uuid1().hex}.{ext}"
    image_path = os.path.join(bucket_path, 'user', str(user.id), unique_filename)
    relative_image_path = os.path.join('user', str(user.id), unique_filename)
    return image_path, relative_image_path