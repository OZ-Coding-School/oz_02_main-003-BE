from config.settings import MEDIA_URL

def get_image_uri(image_uri):
    if image_uri:
        image_uri = image_uri.strip()
        if MEDIA_URL in image_uri:
            return image_uri
        else:
            return MEDIA_URL + image_uri
    return None