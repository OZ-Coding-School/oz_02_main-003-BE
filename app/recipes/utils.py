import os
from django.utils.timezone import now

def upload_image(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"{instance.id}/main_{now().strftime('%Y%m%d%H%M%S')}{filename_ext}"
    return new_filename


def upload_step_image(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    new_filename = f"{now().strftime('%Y%m%d')}_{filename_base}{filename_ext}"
    return os.path.join(new_filename)