from rest_framework import serializers

from eth_wallets.web3_utils import validate_address
from eth_wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('public_address', 'currency')

    public_address = serializers.CharField(max_length=255, required=False)
    currency = serializers.CharField(max_length=10, required=True)

    def validate_currency(self, value):
        if value != 'ETH':
            raise serializers.ValidationError(
                {'error': 'На текущий момент создание кошелька доступно только для ETH'}
            )
        return value


class TransferSerializer(serializers.Serializer):
    _from = serializers.CharField(max_length=255, required=True)
    _to = serializers.CharField(max_length=255, required=True)
    currency = serializers.CharField(max_length=10, required=True)

    def validate__from(self, value):
        if not validate_address(value):
            raise serializers.ValidationError({'error': f'Значение {value} не является ETH адресом'})
        return value

    def validate__to(self, value):
        if not validate_address(value):
            raise serializers.ValidationError({'error': f'Значение {value} не является ETH адресом'})
        return value

    def validate_currency(self, value):
        if value != 'ETH':
            raise serializers.ValidationError({'error': 'На текущий момент трансфер доступен только в ETH'})


class HashSerializer(serializers.Serializer):
    hash = serializers.CharField(max_length=255, required=True)
    nonce = serializers.IntegerField(required=True)
