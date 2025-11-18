from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.service.customer_services import RegistryService


class Registry(APIView):
    def post(self, request: Request, format=None) -> Response:
        service = RegistryService(request.data)
        service.exec()
        return Response(status=201)
