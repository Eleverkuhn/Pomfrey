from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication

from pomfrey_app.services import RegistryService, LoginService, OrderService


class MainView(APIView):
    def get(self, request: Request, format=None) -> Response:
        return Response(status=200)


class RegistryView(APIView):
    def post(self, request: Request) -> Response:
        service = RegistryService(request.data)
        service.exec()
        return Response(status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request: Request) -> Response:
        service = LoginService(request.data)
        response_data = service.exec()
        return Response(response_data, status=status.HTTP_200_OK)


class CustomerPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK)


class OrderView(APIView):
    def post(self, request: Request) -> Response:
        response_data = OrderService(request.data).exec()
        response = Response(response_data, status=status.HTTP_201_CREATED)
        return response
