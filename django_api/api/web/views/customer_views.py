from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication

from api.service.customer_services import RegistryService, LoginService


class Registry(APIView):
    def post(self, request: Request) -> Response:
        service = RegistryService(request.data)
        service.exec()
        return Response(status=status.HTTP_201_CREATED)


class Login(APIView):
    def post(self, request: Request) -> Response:
        service = LoginService(request.data)
        response_data = service.exec()
        return Response(response_data, status=status.HTTP_200_OK)


class CustomerPage(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK)
