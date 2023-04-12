from random import randint
import pytest
from eth_account import Account
from eth_tester import EthereumTester, PyEVMBackend
from web3 import Web3

from eth_wallets.models import Wallet
from eth_wallets.web3_utils import create_eth_wallet, send_eth_transfer_transaction, validate_address

tester = EthereumTester(PyEVMBackend())
web3 = Web3(Web3.EthereumTesterProvider(tester))


@pytest.fixture
def eth_wallet():
    private_key = tester.backend.account_keys[0]
    account = Account.from_key(private_key)
    wallet = Wallet.objects.create(
        public_address=account.address, private_key=private_key, currency='ETH')
    return wallet


@pytest.fixture
def recipient_address():
    return tester.get_accounts()[randint(1, 9)]


def test_create_eth_wallet():
    wallet_info = create_eth_wallet(web3_instance=web3)
    assert len(wallet_info['public_address']) == 42
    assert len(wallet_info['private_key']) == 66


@pytest.mark.django_db
def test_send_eth_transfer_transaction(eth_wallet, recipient_address):
    balance_before = web3.eth.get_balance(recipient_address)
    result = send_eth_transfer_transaction(
        sender_wallet=eth_wallet,
        recipient_address=recipient_address,
        web3_instance=web3
    )
    web3.eth.wait_for_transaction_receipt(result['hash'])
    balance_after = web3.eth.get_balance(recipient_address)
    assert balance_after > balance_before


def test_validate_address(recipient_address):
    assert validate_address(recipient_address, web3_instance=web3)
    assert not validate_address('0x123qwe456', web3_instance=web3)
