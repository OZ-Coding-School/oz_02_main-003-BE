import os
from django.utils.timezone import now


def upload_image(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"recipe/{instance.id}/{filename_base}{filename_ext}"
    return new_filename


import os
def temp_upload_image(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    if hasattr(instance, 'recipe') and instance.recipe:
        new_filename = f"temp/{instance.recipe.id}/{filename_base}{filename_ext}"
    else:
        new_filename = f"temp/{instance.id}/{filename_base}{filename_ext}"
    return new_filename

def upload_step_image(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"{now().strftime('%Y%m%d')}_{filename_base}{filename_ext}"
    return os.path.join(new_filename)
