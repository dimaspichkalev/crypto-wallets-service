from unittest.mock import patch
import pytest
from django.urls import reverse
from rest_framework import status

from eth_wallets.models import Wallet

pytestmark = pytest.mark.django_db


@pytest.fixture
def sender_wallet(db):
    sender_wallet = Wallet.objects.create(currency='ETH',
                                          public_address='0xf259C1B0C4C744c6a55B8eC3dC2eA514d3B0A8D0',
                                          private_key='0xPrivate')
    return sender_wallet


class TestTransferAPIView:
    api_url = reverse("transfer")

    def test_transfer_eth_successful(self, api_client, sender_wallet):
        with patch('eth_wallets.views.send_eth_transfer_transaction') as mock_transfer:
            mock_transfer.return_value = {
                'hash': '1234567890qwerty',
                'nonce': 0
            }
            data = {
                '_from': sender_wallet.public_address,
                '_to': '0x9F396F225685CF672535712F60CcA8A5DD0188Da',
                'currency': 'ETH'
            }
            response = api_client.post(self.api_url, data=data)
            assert response.status_code == status.HTTP_200_OK
            expected = {
                'hash': '1234567890qwerty',
                'nonce': 0
            }
            assert response.data == expected

    def test_transfer_eth_missing_wallet(self, api_client):
        sender_address = '0xf259C1B0C4C744c6a55B8eC3dC2eA514d3B0A8D0'
        data = {
            '_from': sender_address,
            '_to': '0x9F396F225685CF672535712F60CcA8A5DD0188Da',
            'currency': 'ETH'
        }
        response = api_client.post(self.api_url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == f'Адрес - {sender_address} не существует в базе данных'

    def test_transfer_wrong_data(self, api_client):
        data = {
            '_from': '0x222',
            '_to': '0x333',
            'currency': 'AVAX'
        }
        response = api_client.post(self.api_url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        result = response.data
        assert result['_from']['error'] == 'Значение 0x222 не является ETH адресом'
        assert result['_to']['error'] == 'Значение 0x333 не является ETH адресом'
        assert result['currency']['error'] == 'На текущий момент трансфер доступен только в ETH'

    def test_transfer_missing_data(self, api_client):
        response = api_client.post(self.api_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_result = response.data
        assert '_to' in error_result
        assert '_from' in error_result
        assert 'currency' in error_result

    def test_blockchain_fail_data(self, api_client, sender_wallet):
        expected_error_message = {
            'error': 'Не удалось отправить транзакцию в блокчейн, попробуйте позднее.'
        }
        with patch('eth_wallets.views.send_eth_transfer_transaction') as mock_transfer:
            mock_transfer.return_value = expected_error_message
            data = {
                '_from': sender_wallet.public_address,
                '_to': '0x9F396F225685CF672535712F60CcA8A5DD0188Da',
                'currency': 'ETH'
            }
            response = api_client.post(self.api_url, data=data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data == expected_error_message
