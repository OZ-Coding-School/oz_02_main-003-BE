from rest_framework.exceptions import APIException
class CustomException(APIException):
    """
    커스텀 에러

    ---
    """

    def __init__(self, message=None, status=400, code=None, data=None):
        super().__init__()
        self.status = status
        self.message = message
        self.code = code
        self.data = data
