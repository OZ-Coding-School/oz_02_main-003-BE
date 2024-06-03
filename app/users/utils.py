from users.models import User

def get_or_create_social_user(type, id, image=None):
    social_id = f"{type}_{id}"
    data = {
        "social_type": type,
        "social_id": social_id,
        "image": image
    }
    user, _ = User.objects.get_or_create(**data)
    user.nickname = f"{user.id}번째 냉장고"
    user.save()
    return user