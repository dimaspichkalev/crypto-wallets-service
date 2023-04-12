from django.urls import path

from eth_wallets.views import WalletListCreateView, TransferAPIView

urlpatterns = [
    path('', WalletListCreateView.as_view(), name='wallets_list'),
    path('transfer/', TransferAPIView.as_view(), name='transfer'),
]
