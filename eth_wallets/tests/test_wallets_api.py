from unittest.mock import patch
import pytest
from django.urls import reverse
from rest_framework import status

from eth_wallets.models import Wallet

pytestmark = pytest.mark.django_db


@pytest.fixture
def load_wallets(db):
    Wallet.objects.create(currency='ETH', public_address='0xPublic', private_key='0xPrivate')
    Wallet.objects.create(currency='ETH', public_address='0xPublic2', private_key='0xPrivate2')
    Wallet.objects.create(currency='BTC', public_address='3FZbgi29public', private_key='3FZbgi29private')


class TestWalletListView:
    api_url = reverse("wallets_list")

    def test_get_list_of_eth_wallets_query_params(self, api_client, load_wallets):
        response = api_client.get(f'{self.api_url}?currency=ETH')
        assert response.status_code == status.HTTP_200_OK
        result = response.data
        assert len(result) == 2
        assert result[0]['public_address'] == '0xPublic'
        assert 'private_key' not in result[0]

    def test_get_list_of_eth_wallets_body_params(self, api_client, load_wallets):
        data = {'currency': 'ETH'}
        response = api_client.get(self.api_url, data=data)
        assert response.status_code == status.HTTP_200_OK
        result = response.data
        assert len(result) == 2
        assert result[1]['public_address'] == '0xPublic2'
        assert 'private_key' not in result[1]

    def test_get_all_wallets(self, api_client, load_wallets):
        response = api_client.get(self.api_url)
        assert response.status_code == status.HTTP_200_OK
        result = response.data
        assert len(result) == 3
        assert result[2]['currency'] == 'BTC'
        assert 'private_key' not in result[2]

    def test_get_non_existent_currency_wallets(self, api_client, load_wallets):
        data = {'currency': 'SOL'}
        response = api_client.get(self.api_url, data=data)
        assert response.status_code == status.HTTP_200_OK
        result = response.data
        assert len(result) == 0


class TestWalletCreateView:
    api_url = reverse("wallets_list")

    def test_create_eth_wallet_successful(self, api_client):
        with patch('eth_wallets.views.create_eth_wallet') as mock_wallet:
            mock_wallet.return_value = {
                'public_address': '123',
                'private_key': '123prv'
            }
            data = {'currency': 'ETH'}
            response = api_client.post(self.api_url, data=data)
            assert response.status_code == status.HTTP_201_CREATED
            result = response.data
            assert result['public_address'] == '123'
            assert result['currency'] == 'ETH'
            assert 'private_key' not in result

    def test_create_non_eth_wallet(self, api_client):
        data = {'currency': 'SOL'}
        response = api_client.post(self.api_url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        result = response.data
        assert result['currency']['error'] == 'На текущий момент создание кошелька доступно только для ETH'

    def test_create_wallet_without_input(self, api_client):
        response = api_client.post(self.api_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_result = response.data
        assert 'currency' in error_result
