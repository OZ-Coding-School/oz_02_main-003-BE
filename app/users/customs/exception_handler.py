from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import exceptions, status
from common.data.envdata import ACCESS_TOKEN_COOKIE_NAME
from common.exceptions import CustomException
from common.utils.token_handler import TokenManager
from datetime import timedelta


def add_response_actions_by_code(response, exc):
    code = exc.code
    if code in [-498]:
        response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME)

    if code in [-401]:
        new_access_token = str(TokenManager.get_new_access_token(exc.data["user_id"]))
        response.set_cookie(
            ACCESS_TOKEN_COOKIE_NAME,
            new_access_token,
            max_age=timedelta(days=30),
            httponly=True,
            domain=exc.data["domain"]
        )


def custom_exception_handler(exc, context):
    if type(exc) is CustomException:
        response = Response(
            data=exc.message,
            status=exc.status,
        )
        add_response_actions_by_code(response, exc)
    else:
        response = exception_handler(exc, context)

    if response is None:
        response = Response(
            {"status": 500, "message": "알수 없는 오류", "error": str(exc)}, status=500
        )

    # Now add the HTTP status code to the response.
    # if response is not None:
    #     response.data['status_code'] = response.status_code
    return response
