from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from logger.setup import LoggingConfig


class Registry(APIView):
    def post(self, request: Request, format=None) -> Response:
        logger = LoggingConfig().get_logger()
        logger.debug(request.body)
        return Response(status=201)
