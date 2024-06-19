from users.models import User_refresh_token
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files import File
from io import BytesIO
from config import settings
import urllib.request


User = get_user_model()

import os
import uuid


def generate_image_path(user, ext):
    BUCKET_PATH = settings.BUCKET_PATH
    unique_filename = f"{user.nickname}_{uuid.uuid1().hex}.{ext}"
    image_path = os.path.join(BUCKET_PATH, "user", str(user.id), unique_filename)
    relative_image_path = os.path.join("user", str(user.id), unique_filename)
    return image_path, relative_image_path


from django.core.files.base import ContentFile
from botocore.exceptions import NoCredentialsError


def get_image_from_url(url):
    # 이미지 URL에서 이미지 데이터 가져오기
    with urllib.request.urlopen(url) as resp:
        image_data = resp.read()

    return ContentFile(image_data)


def upload_image(image_file, image_path):
    try:
        settings.s3_client.upload_fileobj(
            image_file,
            settings.AWS_STORAGE_BUCKET_NAME,
            image_path,
            ExtraArgs={
                "ContentType": "image/jpeg",
            },
        )

        return True

    except NoCredentialsError:
        return False


# http://127.0.0.1:8000/api/v1/users/auth/login?social=google&dev=1


def get_or_create_social_user(type, id, image_url=None):
    social_id = f"{type}_{id}"
    data = {"social_type": type, "social_id": social_id}
    user, created = User.objects.get_or_create(**data)
    if created:
        user.nickname = f"{user.id}번째 냉장고"
        if image_url:
            image_file = get_image_from_url(image_url)
            image_path, relative_image_path = generate_image_path(user, "jpeg")
            if upload_image(image_file, image_path):
                user.image = relative_image_path
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


from common.data.envdata import ACCESS_TOKEN_COOKIE_NAME
from datetime import timedelta

PUBLIC_URL = "ndd.life"


def get_user_remote(request):
    return request.META.get("REMOTE_ADDR", None)

def get_user_host(request):
    """유저의 호스트 가져오기"""
    return request.META.get("HTTP_HOST", None)


def get_is_product(remote):
    """host가 배포된 환경인지 로컬인지 판단"""
    return remote == PUBLIC_URL


def get_cookie_domain(host):
    if host == PUBLIC_URL:
        return f".{PUBLIC_URL}"
    return host.split(":")[0]


def get_cookie_settings(request, token):
    host = get_user_host(request)
    is_product = get_is_product(host)

    cookie_settings = {
        "key": ACCESS_TOKEN_COOKIE_NAME,
        "max_age": timedelta(days=30),
        "value": token,
        "httponly": True,
        "domain": get_cookie_domain(host),
        "secure": is_product
    }

    return cookie_settings


def set_jwt_cookie(request, response, token):
    response.set_cookie(**get_cookie_settings(request, token))
