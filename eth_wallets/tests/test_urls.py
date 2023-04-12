from django.urls import resolve, reverse

from eth_wallets.views import WalletListCreateView, TransferAPIView


def test_wallets_url():
    url = reverse('wallets_list')
    assert url == '/api/wallets/'
    assert resolve(url).func.view_class == WalletListCreateView


def test_transfer_url():
    url = reverse('transfer')
    assert url == '/api/wallets/transfer/'
    assert resolve(url).func.view_class == TransferAPIView
