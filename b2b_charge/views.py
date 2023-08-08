from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import (
    MerchantSerializer,
    TransactionLogSerializer,
    BuyChargeSerializer,
)
from .models import Merchant, TransactionLog


class MerchantViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = MerchantSerializer
    queryset = Merchant.objects.filter(is_active=True)

    @action(
        methods=["POST"],
        url_path="add-credit",
        url_name="add-credit",
        permission_classes=[AllowAny],
        detail=True,
    )
    def add_credit(self, request, pk):
        """
        The view that adds credit to merchant.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        merchant = get_object_or_404(Merchant, id=pk)
        credit = validated_data["credit"]
        try:
            merchant.transaction(action="add_credit", amount=credit, phone=None)
        except Exception as e:
            return Response(
                {"message": "Cannot execute transaction due to : %s" % (e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Successfully added credits.",
            },
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["POST"],
        url_path="buy-charge",
        url_name="buy-charge",
        permission_classes=[AllowAny],
        detail=True,
    )
    def buy_charge(self, request, pk):
        """
        The view that buys charge for a particular phonenumber using a particular merchant.
        """
        serializer = BuyChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        phone = validated_data["phone"]
        amount = validated_data["amount"]
        merchant = get_object_or_404(Merchant, id=pk)

        try:
            merchant.transaction(action="subtract_credit", phone=phone, amount=amount)
        except Exception as e:
            return Response(
                {"message": "Cannot execute transaction due to : %s" % (e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "message": "Successfully bought charge.",
            },
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["GET"],
        url_path="get-credit",
        url_name="get-credit",
        permission_classes=[AllowAny],
        detail=True,
    )
    def get_credit(self, request, pk):
        """
        The view that returns overall credit for a particular merchant.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        merchant = get_object_or_404(Merchant, id=pk)
        return Response(
            {
                "merchant_id": merchant.id,
                "credit": merchant.get_credit(),
            },
            status=status.HTTP_200_OK,
        )
