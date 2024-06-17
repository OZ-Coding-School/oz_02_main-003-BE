from config.settings import MEDIA_URL
def get_image_uri(image_uri):
    if image_uri:
        image_uri = image_uri.strip()  
    return MEDIA_URL + image_uri if image_uri else None