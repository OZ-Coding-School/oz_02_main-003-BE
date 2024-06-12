import os
from django.utils.timezone import now
from config.settings import BUCKET_PATH

def copy_file(source_key, destination_key):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    copy_source = {'Bucket': bucket_name, 'Key': source_key}
    s3_client.copy_object(CopySource=copy_source, Bucket=bucket_name, Key=destination_key)

def upload_image(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"{BUCKET_PATH}recipe/{instance.id}/{filename_base}{filename_ext}"
    return new_filename


def upload_image_step(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"{BUCKET_PATH}recipe/{instance.recipe.id}/{filename_base}{filename_ext}"
    return new_filename




from django.conf import settings
import boto3


import uuid

import base64
from django.core.files.base import ContentFile

def create_file(type_data, ext, imgstr, order=None):
    file_name = type_data
    if order:
        file_name += f"_{order}"
    file_name += f"_{uuid.uuid1().hex}.{ext}"
    return ContentFile(base64.b64decode(imgstr), name=f"{file_name}")


def temp_upload_image(instance, filename):
    new_filename = f"{BUCKET_PATH}temp/"
    new_filename += (
        str(instance.recipe.id)
        if hasattr(instance, "step") and instance.recipe
        else str(instance.id)
    )
    new_filename += "/" + filename
    return new_filename
