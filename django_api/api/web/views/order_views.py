from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.service.order_services import OrderService


class OrderView(APIView):
    def post(self, request: Request) -> Response:
        response_data = OrderService(request.data).exec()
        response = Response(response_data, status=status.HTTP_201_CREATED)
        return response
