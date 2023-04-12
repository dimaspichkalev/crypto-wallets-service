from web3 import Web3, HTTPProvider
from requests.exceptions import ConnectionError as RequestsConnectionError

from eth_wallets.models import Wallet
from eth_wallets.constants import INFURA_URL, GAS_LIMIT, GAS_PRICE


class Web3Provider:
    __instance = None

    @staticmethod
    def get_instance():
        if Web3Provider.__instance is None:
            Web3Provider()
        return Web3Provider.__instance

    def __init__(self, provider=None):
        if Web3Provider.__instance is not None:
            raise Exception("Only one instance of Web3Provider is allowed.")
        else:
            if not provider:
                provider = HTTPProvider(INFURA_URL)
            self.w3 = Web3(provider)
            Web3Provider.__instance = self


def create_eth_wallet(web3_instance=None):
    if not web3_instance:
        web3_instance = Web3Provider.get_instance().w3
    account = web3_instance.eth.account.create()
    public_address = account.address
    private_key = account.key.hex()
    result = {
        'public_address': public_address,
        'private_key': private_key
    }
    return result


def validate_address(address: str, web3_instance=None):
    if not web3_instance:
        web3_instance = Web3Provider.get_instance().w3
    return web3_instance.is_address(address)


def send_eth_transfer_transaction(sender_wallet: Wallet, recipient_address: str, web3_instance=None):
    if not web3_instance:
        web3_instance = Web3Provider.get_instance().w3
    try:
        transaction = {
            'to': recipient_address,
            'gas': GAS_LIMIT,
            'gasPrice': web3_instance.to_wei(GAS_PRICE, 'gwei'),
            'nonce': web3_instance.eth.get_transaction_count(sender_wallet.public_address)
        }

        sender_balance = web3_instance.eth.get_balance(sender_wallet.public_address)
        max_amount = sender_balance - (transaction['gasPrice'] * transaction['gas'])
        if max_amount < 0:
            return {'error': 'Недостаточно ETH для совершения транзакции'}

        transaction.update({'value': max_amount})
        signed_tx = web3_instance.eth.account.sign_transaction(transaction, sender_wallet.private_key)
        tx_hash = web3_instance.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_info = {
            'hash': tx_hash.hex(),
            'nonce': transaction['nonce']
        }
        return tx_info
    except RequestsConnectionError:
        return {'error': 'Не удалось отправить транзакцию в блокчейн, попробуйте позднее.'}
    except ValueError as e:
        return {'error': e.args[0]}
