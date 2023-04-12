from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from eth_wallets.models import Wallet
from eth_wallets.serializers import HashSerializer, TransferSerializer, WalletSerializer
from eth_wallets.web3_utils import create_eth_wallet, send_eth_transfer_transaction


class WalletListCreateView(ListCreateAPIView):
    serializer_class = WalletSerializer

    def get_queryset(self):
        currency = self.request.query_params.get('currency') or self.request.data.get('currency')

        if currency:
            queryset = Wallet.objects.filter(currency=currency)
        else:
            queryset = Wallet.objects.all()

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet_info = create_eth_wallet()
        wallet_info['currency'] = serializer.validated_data['currency']
        wallet = Wallet.objects.create(**wallet_info)
        wallet.save()
        serializer = self.get_serializer(wallet)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        operation_summary="List of cryptocurrency wallets",
        operation_description="Show list of wallets by currency or all of them",
        query_serializer=WalletSerializer
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create wallet for particular cryptocurrency",
        operation_description="Create ETH wallet and save it to the database",
        request_body=WalletSerializer,
        responses={
            status.HTTP_201_CREATED: WalletSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request"
        },
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TransferAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Transfer money from one address to another",
        operation_description="Send a transaction to a blockchain from one address (from db) to any other with all ETH",
        request_body=TransferSerializer,
        responses={
            status.HTTP_200_OK: HashSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request"
        },
    )
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_address = serializer.validated_data['_from']
        recipient_address = serializer.validated_data['_to']
        sender_wallet = Wallet.objects.filter(public_address=sender_address).first()

        if not sender_wallet:
            error = {'error': f'Адрес - {sender_address} не существует в базе данных'}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

        transfer_result = send_eth_transfer_transaction(sender_wallet, recipient_address)
        if 'error' in transfer_result:
            return Response(data=transfer_result,
                            status=status.HTTP_400_BAD_REQUEST,
                            headers=self.default_response_headers)
        hash_serializer = HashSerializer(data=transfer_result)
        hash_serializer.is_valid()
        return Response(hash_serializer.data, status=status.HTTP_200_OK)
