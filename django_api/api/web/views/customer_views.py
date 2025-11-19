from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.service.customer_services import RegistryService, LoginService


class Registry(APIView):
    def post(self, request: Request) -> Response:
        service = RegistryService(request.data)
        service.exec()
        return Response(status=201)


class Login(APIView):
    def post(self, request: Request) -> Response:
        service = LoginService(request.data)
        response_data = service.exec()
        return Response(response_data, status=200)
