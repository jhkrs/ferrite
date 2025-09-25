from eth_account.datastructures import SignedTransaction
from hexbytes import HexBytes

from ferrite import sign_transaction

def sign_transaction_wrapper(transaction_dict: dict, private_key: str) -> SignedTransaction:
    signed_tx_dict = sign_transaction(transaction_dict, private_key)
    return SignedTransaction(
        rawTransaction=HexBytes(signed_tx_dict['rawTransaction']),
        hash=HexBytes(signed_tx_dict['hash']),
        r=int.from_bytes(signed_tx_dict['r'], 'big'),
        s=int.from_bytes(signed_tx_dict['s'], 'big'),
        v=signed_tx_dict['v']
    )

class FerriteAccount:
    def sign_transaction(self, transaction_dict: dict, private_key: str) -> SignedTransaction:
        return sign_transaction_wrapper(transaction_dict, private_key)

    def __getattr__(self, name):
        from eth_account import Account
        return getattr(Account, name)

ferrite_account = FerriteAccount()