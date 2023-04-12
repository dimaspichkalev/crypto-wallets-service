from eth_wallets.serializers import WalletSerializer, TransferSerializer


def test_wallet_serializer():
    data = {
        'public_address': 'public_123',
        'private_key': 'private_123',
        'currency': 'ETH'
    }
    expected_data = {
        'currency': data['currency'],
        'public_address': data['public_address']
    }
    serializer = WalletSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.data == expected_data


def test_wallet_serializer_wrong_data():
    data = {
        'public_address': 123,
        'private_key': 123,
        'currency': 'AVAX'
    }
    serializer = WalletSerializer(data=data)
    assert not serializer.is_valid()


def test_transfer_serializer_wrong_data():
    data = {
        '_from': '0x222',
        '_to': '0x333',
        'currency': 'AVAX'
    }
    serializer = TransferSerializer(data=data)
    assert not serializer.is_valid()
