import os

GOOGLE_OAUTH2_CLIENT_ID = os.environ.get("GOOGLE_OAUTH2_CLIENT_ID")
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH2_CLIENT_SECRET")

KAKAO_OAUTH2_CLIENT_ID = os.environ.get("KAKAO_OAUTH2_CLIENT_ID")
KAKAO_OAUTH2_CLIENT_SECRET = os.environ.get("KAKAO_OAUTH2_CLIENT_SECRET")

HOST = os.environ.get("HOST")

OAUTH2_CLIENT_ID = {
    "kakao": os.environ.get("KAKAO_OAUTH2_CLIENT_ID"),
    "google": os.environ.get("GOOGLE_OAUTH2_CLIENT_ID"),
}

OAUTH2_CLIENT_SECRET = {
    "kakao": os.environ.get("KAKAO_OAUTH2_CLIENT_SECRET"),
    "google": os.environ.get("GOOGLE_OAUTH2_CLIENT_SECRET")
}
