import os
from django.utils.timezone import now


def upload_image(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"recipe/{instance.id}/{filename_base}{filename_ext}"
    return new_filename

def upload_image_step(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"recipe/{instance.recipe.id}/{filename_base}{filename_ext}"
    return new_filename

def temp_upload_image(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    if hasattr(instance, 'step') and instance.recipe:
        new_filename = f"temp/{instance.recipe.id}/{filename_base}{filename_ext}"
    else:
         new_filename = f"temp/{instance.id}/{filename_base}{filename_ext}"
    return new_filename


